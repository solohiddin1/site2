
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.company.middleware import get_logger

from .models import ProductImage
from .utils import compress_image

logger = get_logger()


def _compress_product_image(instance: ProductImage) -> None:
    try:
        import os

        if not instance.image:
            return

        # Keep original dimensions, only reduce file size.
        # Generate a single optimized derivative and use it as the canonical processed file.
        image_desktop = compress_image(
            instance.image,
            sizes=None,
            format="WEBP",
            quality=82,
            keep_dimensions=True,
        )

        # Save generated files without triggering model save recursion.
        instance.image_desktop.save(image_desktop.name, image_desktop, save=False)
        ProductImage.objects.filter(pk=instance.pk).update(
            image_desktop=instance.image_desktop,
            image_mobile=None,
        )

        old_paths = {
            'original': getattr(instance, '_old_image', None),
            'desktop': getattr(instance, '_old_image_desktop', None),
            'mobile': getattr(instance, '_old_image_mobile', None),
        }

        for img_type, old_path in old_paths.items():
            if old_path and os.path.exists(old_path):
                try:
                    os.remove(old_path)
                    logger.info(f"🗑️  Deleted old {img_type} image: {old_path}")
                except Exception as delete_error:
                    logger.warning(f"⚠️  Failed to delete old {img_type} image: {delete_error}")

        logger.info(f"✅ ProductImage #{instance.pk} compressed successfully")
    except Exception as e:
        logger.exception(f"❌ Error compressing ProductImage #{instance.pk}: {e}")


@receiver(pre_save, sender=ProductImage)
def track_product_image_changes(sender, instance, **kwargs):
    print(f"🔍 Tracking changes for ProductImage #{instance.pk}")

    if not instance.pk:
        # New object: let post_save handle compression after PK exists.
        instance._image_changed = bool(instance.image)
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
        instance._image_changed = old_instance.image != instance.image

        if instance._image_changed:
            instance._old_image = old_instance.image.path if old_instance.image else None
            instance._old_image_desktop = old_instance.image_desktop.path if old_instance.image_desktop else None
            instance._old_image_mobile = old_instance.image_mobile.path if old_instance.image_mobile else None
    except sender.DoesNotExist:
        instance._image_changed = bool(instance.image)


@receiver(post_save, sender=ProductImage)
def compress_product_image_after_save(sender, instance, created, **kwargs):
    if not instance.image:
        return

    should_compress = created or getattr(instance, '_image_changed', False)
    if not should_compress:
        return

    transaction.on_commit(lambda: _compress_product_image(instance))

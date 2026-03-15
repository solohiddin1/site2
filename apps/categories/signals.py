import os

from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.company.middleware import get_logger
from apps.products.utils import compress_image

from .models import Category, SubCategory

logger = get_logger()


def _compress_category_image(instance, image_attr: str, compressed_attr: str):
    try:
        image_file = getattr(instance, image_attr, None)
        if not image_file:
            return

        compressed = compress_image(
            image_file,
            sizes=None,
            format="WEBP",
            quality=82,
            keep_dimensions=True,
        )

        getattr(instance, compressed_attr).save(compressed.name, compressed, save=False)
        type(instance).objects.filter(pk=instance.pk).update(
            **{compressed_attr: getattr(instance, compressed_attr)}
        )

        old_path_attr = f"_old_{compressed_attr}_path"
        old_compressed_path = getattr(instance, old_path_attr, None)
        if old_compressed_path and os.path.exists(old_compressed_path):
            try:
                os.remove(old_compressed_path)
            except Exception as delete_error:
                logger.warning(f"⚠️ Failed to delete old compressed image: {delete_error}")

        logger.info(f"✅ {type(instance).__name__} #{instance.pk} image compressed")
    except Exception as e:
        logger.exception(f"❌ Error compressing {type(instance).__name__} #{instance.pk}: {e}")


@receiver(pre_save, sender=Category)
def track_category_image_changes(sender, instance, **kwargs):
    if not instance.pk:
        instance._image_changed = bool(instance.image)
        instance._second_image_changed = bool(instance.second_image)
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
        instance._image_changed = old_instance.image != instance.image
        instance._second_image_changed = old_instance.second_image != instance.second_image

        if instance._image_changed:
            instance._old_image_compressed_path = (
                old_instance.image_compressed.path if old_instance.image_compressed else None
            )
        if instance._second_image_changed:
            instance._old_second_image_compressed_path = (
                old_instance.second_image_compressed.path if old_instance.second_image_compressed else None
            )
    except sender.DoesNotExist:
        instance._image_changed = bool(instance.image)
        instance._second_image_changed = bool(instance.second_image)


@receiver(post_save, sender=Category)
def compress_category_image_after_save(sender, instance, created, **kwargs):
    should_compress_main = (created and bool(instance.image)) or getattr(instance, '_image_changed', False)
    should_compress_second = (created and bool(instance.second_image)) or getattr(instance, '_second_image_changed', False)

    if should_compress_main:
        transaction.on_commit(lambda: _compress_category_image(instance, 'image', 'image_compressed'))

    if should_compress_second:
        transaction.on_commit(lambda: _compress_category_image(instance, 'second_image', 'second_image_compressed'))


@receiver(pre_save, sender=SubCategory)
def track_subcategory_image_changes(sender, instance, **kwargs):
    if not instance.pk:
        instance._image_changed = bool(instance.image)
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
        instance._image_changed = old_instance.image != instance.image
        if instance._image_changed:
            instance._old_compressed_path = (
                old_instance.image_compressed.path if old_instance.image_compressed else None
            )
    except sender.DoesNotExist:
        instance._image_changed = bool(instance.image)


@receiver(post_save, sender=SubCategory)
def compress_subcategory_image_after_save(sender, instance, created, **kwargs):
    if not instance.image:
        return

    should_compress = created or getattr(instance, '_image_changed', False)
    if not should_compress:
        return

    transaction.on_commit(lambda: _compress_category_image(instance, 'image', 'image_compressed'))



from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductImage
from .utils import compress_image
from apps.company.middleware import get_logger

logger = get_logger()

@receiver(post_save, sender=ProductImage)
def update_product_image_urls(sender, instance, created, **kwargs):
    """
    Compress and create thumbnails when ProductImage is created or updated.
    If image is updated, remove old images before saving new ones.
    """
    from django.db import transaction
    
    # Skip if no image or if already processing thumbnails
    if not instance.image or getattr(instance, '_skip_thumb', False):
        return
    
    # Only process if it's a new image or the image field was changed
    should_process = created or getattr(instance, '_image_changed', False)
    
    if not should_process:
        return
    
    # Use transaction.on_commit to run after the current transaction completes
    def compress_and_save():
        try:
            import os
            # Set flag to prevent recursion
            instance._skip_thumb = True
            
            # 1. Compress for desktop detail view - 1200x900
            image_desktop = compress_image(
                instance.image,
                sizes=(1200, 900),
                format="WEBP",
                quality=100
            )
            instance.image_desktop.save(image_desktop.name, image_desktop, save=False)
            
            # 4. Compress for mobile non-retina (product list) - 800x600
            image_mobile = compress_image(
                instance.image,
                sizes=(800, 600),
                format="WEBP",
                quality=100
            )
            instance.image_mobile.save(image_mobile.name, image_mobile, save=False)
            
            # 5. Compress for miniatura thumbnail - 400x300
            image_thumb_miniatura = compress_image(
                instance.image,
                sizes=(400, 300),
                format="WEBP",
                quality=100
            )
            instance.image_thumb_miniatura.save(image_thumb_miniatura.name, image_thumb_miniatura, save=False)
            
            # Update all thumbnail fields - this happens in its own transaction
            ProductImage.objects.filter(pk=instance.pk).update(
                image_desktop=instance.image_desktop,
                image_mobile=instance.image_mobile,
                image_thumb_miniatura=instance.image_thumb_miniatura
            )
            
            # Delete old images after new ones are saved
            old_paths = {
                'original': getattr(instance, '_old_image', None),
                'desktop': getattr(instance, '_old_image_desktop', None),
                'mobile': getattr(instance, '_old_image_mobile', None),
                'miniatura': getattr(instance, '_old_image_thumb_miniatura', None),
            }
            
            for img_type, old_path in old_paths.items():
                if old_path:
                    try:
                        if os.path.exists(old_path):
                            os.remove(old_path)
                            logger.info(f"🗑️  Deleted old {img_type} image: {old_path}")
                    except Exception as delete_error:
                        logger.warning(f"⚠️  Failed to delete old {img_type} image: {delete_error}")
            
            logger.info(f"✅ ProductImage #{instance.pk} compressed successfully (all sizes)")
            
        except Exception as e:
            logger.exception(f"❌ Error compressing ProductImage #{instance.pk}: {e}")
    
    # Schedule compression to run after the current transaction commits
    transaction.on_commit(compress_and_save)

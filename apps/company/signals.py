from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BannerImages as Banner
from apps.products.utils import compress_image
from apps.company.middleware import get_logger
from django.db import transaction

logger = get_logger()

@receiver(post_save, sender=Banner)
def update_product_image_urls(sender, instance, created, **kwargs):
    """
    Compress and create thumbnails when Banner is created or updated.
    If image is updated, remove old images before saving new ones.
    """
    
    # Skip if no image or if already processing thumbnails
    print("Banner post_save signal triggered...")
    if not instance.image or getattr(instance, '_skip_thumb', False):
        print("No image found or skipping thumbnail processing.")
        return
    
    # Only process if it's a new image or the image field was changed
    # should_process = created or getattr(instance, '_image_changed', False)
    
    # if not should_process:
    #     print("No changes to image detected; skipping compression.")
    #     return
    
    # Use transaction.on_commit to run after the current transaction completes
    print("Scheduling banner image compression task...")
    def compress_and_save():
        try:
            import os
            # Set flag to prevent recursion
            instance._skip_thumb = True
            
            # 1. Compress for desktop detail view - 1200x900
            image_desktop = compress_image(
                instance.image,
                sizes=(1920, 900),
                format="WEBP",
                quality=100
            )
            instance.image_desktop.save(image_desktop.name, image_desktop, save=False)
            
            # 4. Compress for mobile non-retina (product list) - 800x600
            image_mobile = compress_image(
                instance.image,
                sizes=(370, 650),
                format="WEBP",
                quality=100
            )
            instance.image_mobile.save(image_mobile.name, image_mobile, save=False)
            
            # Update all thumbnail fields - this happens in its own transaction
            Banner.objects.filter(pk=instance.pk).update(
                image_desktop=instance.image_desktop,
                image_mobile=instance.image_mobile
            )
            
            # Delete old images after new ones are saved
            old_paths = {
                'original': getattr(instance, '_old_image', None),
                'desktop': getattr(instance, '_old_image_desktop', None),
                'mobile': getattr(instance, '_old_image_mobile', None),
            }
            
            for img_type, old_path in old_paths.items():
                if old_path:
                    try:
                        if os.path.exists(old_path):
                            os.remove(old_path)
                            logger.info(f"🗑️  Deleted old {img_type} image: {old_path}")
                    except Exception as delete_error:
                        logger.warning(f"⚠️  Failed to delete old {img_type} image: {delete_error}")
            
            logger.info(f"✅ Banner #{instance.pk} compressed successfully (all sizes)")
            
        except Exception as e:
            logger.exception(f"❌ Error compressing Banner #{instance.pk}: {e}")
    
    # Schedule compression to run after the current transaction commits
    transaction.on_commit(compress_and_save)

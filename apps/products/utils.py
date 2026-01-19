import os
import io
from PIL import Image
from django.core.files.base import ContentFile

"""for product model"""
def compress_image(
        image_file, 
        sizes: tuple, 
        format: str, 
        quality: int
        ):
    """
        image_file: Django ImageField file
        size: (width, height)
        format: WEBP / JPEG / PNG
    """
    img = Image.open(image_file)
    img = img.convert("RGB")  # Ensure image is in RGB mode
    resized = img.resize(sizes, Image.LANCZOS)  # Resize to given sizes
    
    buffer = io.BytesIO()
    resized.save(buffer, format=format, quality=quality)
    ext = format.lower()
    # name = image_file.name.rsplit(".", 1)[0]
    name, _ = os.path.splitext(os.path.basename(image_file.name)) # Get name without extension
    filename = f"{name}_{sizes[0]}x{sizes[1]}.{ext}"

    return ContentFile(buffer.getvalue(), name=filename)

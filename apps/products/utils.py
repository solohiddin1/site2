import os
import io
import requests
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings

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
    print(f"Compressing image {image_file.name} to size {sizes} in format {format}...")
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


def send_product_inquiry_telegram(name, phone_number, message, product_data=None):
    TELEGRAM_TOKEN = settings.TELEGRAM_TOKEN
    CHAT_ID = settings.CHAT_ID
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    inquiry_text = (
        f"<b>🛒 Yangi Mahsulot So'rovi</b>\n\n"
        f"<b>👤 Ism:</b> {name}\n"
        f"<b>📞 Telefon:</b> {phone_number}\n"
        f"<b>💬 Xabar:</b> {message}\n"
    )
    
    if product_data:
        inquiry_text += (
            f"\n<b>📦 Mahsulot Ma'lumotlari:</b>\n"
            f"<b>🔹 Nomi:</b> {product_data.get('name')}\n"
            f"<b>🔹 Artikul:</b> {product_data.get('sku')}\n"
            f"<b>🔗 Link:</b> <a href=\"{product_data.get('url')}\">Ko'rish</a>\n"
            f"<b>🔗 Link:</b> {product_data.get('url')}\n"
        )
        
    payload = {
        "chat_id": CHAT_ID,
        "text": inquiry_text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    return response
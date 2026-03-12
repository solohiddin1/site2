import asyncio
import inspect
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from googletrans import Translator
from django.utils.text import slugify
from django_json_widget.widgets import JSONEditorWidget
import uuid

from apps.categories.models import SubCategory, BaseModel


translator = Translator()


def get_unique_code():
    return str(uuid.uuid4().int)[:4]


class Product(TranslatableModel, BaseModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True),
    )

    slug = models.SlugField(
        max_length=255,
        blank=True,
        null=True,
        allow_unicode=True,
        unique=True
    )
    unique_code = models.CharField(max_length=50, default=get_unique_code, blank=True, null=True)
    sku = models.CharField(max_length=100, blank=True, null=True, unique=True)
    warranty_months = models.IntegerField(blank=True, null=True, default=12)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['-created_at']

    def __str__(self):
        return self.safe_translation_getter('name') or 'Unnamed Product'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # Ensure we have a slug before saving if possible, or save first then update
        base_lang = 'uz'
        self.set_current_language(base_lang)
        
        # If name is available (e.g. set on the instance), try to generate slug
        if not self.slug and self.safe_translation_getter('name'):
             self.slug = slugify(f"{self.safe_translation_getter('name')}-{self.unique_code}", allow_unicode=True)

        super().save(*args, **kwargs)

        target_langs = ['en', 'ru']

        # Logic to auto-translate name/description if missing
        try:
            # force fetch from db or cache
            base_translation = self.translations.get(language_code=base_lang)
        except Exception as e:
            # If we just saved it, it might be in memory? 
            # If base translation is missing in DB, we can't translate to others.
            return

        for lang in target_langs:
            if self.translations.filter(language_code=lang).exists():
                continue
            try:
                res_name = translator.translate(base_translation.name, src=base_lang, dest=lang)
                if inspect.isawaitable(res_name):
                    translated_name = asyncio.run(res_name).text
                else:
                    translated_name = res_name.text

                res_desc = translator.translate(base_translation.description, src=base_lang, dest=lang)
                if inspect.isawaitable(res_desc):
                    translated_desc = asyncio.run(res_desc).text
                else:
                    translated_desc = res_desc.text

                # Slug is now shared, no need to translate it.

                self.create_translation(
                    language_code=lang,
                    name=translated_name,
                    description=translated_desc,
                )
                print(f"✅ Translated {lang}: {translated_name}")
            except Exception as e:
                print(f"❌ Translation failed for {lang}: {e}")


class ProductImage(BaseModel):
    """Multiple images per product with ordering"""
    product = models.ForeignKey(Product, related_name='images', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_desktop = models.ImageField(upload_to='products/desktop/', blank=True, null=True)
    image_mobile = models.ImageField(upload_to='products/mobile/', blank=True, null=True)
    alt = models.CharField(max_length=255, blank=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordering', 'id']
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")

    def __str__(self):
        return f"Image {self.pk} for Product {self.product_id}"


class ProductLongDesc(TranslatableModel, BaseModel):
    """Long description for products"""
    translations = TranslatedFields(
        long_desc=models.TextField(blank=True, null=True),
    )

    product = models.ForeignKey(
        Product,
        related_name='long_desc',
        verbose_name=_("Product Long Description"),
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("Product Long Description")
        verbose_name_plural = _("Product Long Descriptions")

    def __str__(self):
        return f"Long Desc for {self.product}"




class ProductPackageContentImages(TranslatableModel, BaseModel):
    """Package content images for products"""
    translations = TranslatedFields(
        image=models.ImageField(upload_to='products/package_content/', blank=True, null=True)
    )

    product = models.ForeignKey(
        Product,
        related_name='package_content_images',
        verbose_name=_("Product Package Content Images"),
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("Product Package Content Image")
        verbose_name_plural = _("Product Package Content Images")

    def __str__(self):
        return f"Package Image for {self.product}"


class ProductSpecs(TranslatableModel, BaseModel):
    """Product specifications stored as JSON"""
    translations = TranslatedFields(
        specs=models.JSONField(_("Specifications"), encoder=None, decoder=None, blank=True, null=True)
    )

    product = models.ForeignKey(
        Product,
        related_name='specs',
        verbose_name=_("Product Specs"),
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("Product Specification")
        verbose_name_plural = _("Product Specifications")

    def __str__(self):
        specs_data = self.safe_translation_getter('specs', any_language=True)
        if specs_data is not None:
            return str(specs_data)
        return "Product specs"

    def formfield(self, **kwargs):
        kwargs["widget"] = JSONEditorWidget
        return super().formfield(**kwargs)


class ProductSpecsTemplate(TranslatableModel, BaseModel):
    """Template for product specifications"""
    translations = TranslatedFields(
        name=models.CharField(max_length=255, blank=True, null=True),
        specs=models.JSONField(_("Specifications Template"), encoder=None, decoder=None, blank=True, null=True)
    )

    class Meta:
        verbose_name = _("Product Specs Template")
        verbose_name_plural = _("Product Specs Templates")

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or "Unnamed Template"


class TopProduct(BaseModel):
    """Featured products for homepage"""
    product = models.ForeignKey(Product, related_name='top_products', on_delete=models.CASCADE, blank=True, null=True)
    ordering = models.PositiveIntegerField(default=0, help_text=_("Display order (lower numbers appear first)"))

    class Meta:
        verbose_name = _("Top Product")
        verbose_name_plural = _("Top Products")
        ordering = ['ordering', '-created_at']

    def __str__(self):
        return f"Top Product: {self.product}"
    

class NewArrivals(BaseModel):
    """New arrival products for homepage"""
    product = models.ForeignKey(Product, related_name='new_arrivals', on_delete=models.CASCADE, blank=True, null=True)
    ordering = models.PositiveIntegerField(default=0, help_text=_("Display order (lower numbers appear first)"))

    class Meta:
        verbose_name = _("New Arrival")
        verbose_name_plural = _("New Arrivals")
        ordering = ['ordering', '-created_at']

    def __str__(self):
        return f"New Arrival: {self.product}"



class ProductUsageItem(TranslatableModel, BaseModel):
    """Flexible usage item: handles image, video, or social links"""
    
    # We keep the translations here if the client wants 
    # specific captions for each video/image
    translations = TranslatedFields(
        caption=models.CharField(max_length=255, blank=True, null=True),
    )

    product = models.ForeignKey(
        Product,
        related_name='usage_media', # Changed for clarity
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    # The 'Source' determines which field below is used
    MEDIA_TYPE_CHOICES = [
        ("image", "Image Upload"),
        ("external", "Link (YouTube/Instagram)"),
    ]
    media_type = models.CharField(max_length=16, choices=MEDIA_TYPE_CHOICES, default="image")
    
    # The actual data fields
    file = models.FileField(upload_to="products/usage/", blank=True, null=True, help_text="Upload image or video file")
    external_url = models.URLField(blank=True, null=True, help_text="YouTube yoki Instagram ning url linkini kiriting")
    
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordering"]
        verbose_name = _("Product Usage Media")

    def __str__(self):
        return f"{self.file} for {self.product.name}"

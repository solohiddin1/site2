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
        slug=models.SlugField(
            max_length=255,
            blank=True,
            null=True,
            allow_unicode=True
        ),
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
        super().save(*args, **kwargs)

        base_lang = 'uz'
        target_langs = ['en', 'ru']

        self.set_current_language(base_lang)
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.unique_code}", allow_unicode=True)
            super().save()

        try:
            base_translation = self.translations.get(language_code=base_lang)
        except Exception as e:
            print(f"⚠️ No base translation found for {base_lang}: {e}")
            return

        for lang in target_langs:
            if self.translations.filter(language_code=lang).exists():
                continue
            try:
                translated_name = translator.translate(base_translation.name, src=base_lang, dest=lang).text
                translated_desc = translator.translate(base_translation.description, src=base_lang, dest=lang).text
                translated_slug = slugify(f"{translated_name}-{self.unique_code}", allow_unicode=True)

                self.create_translation(
                    language_code=lang,
                    name=translated_name,
                    description=translated_desc,
                    slug=translated_slug
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
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("Product Long Description")
        verbose_name_plural = _("Product Long Descriptions")

    def __str__(self):
        return f"Long Desc for {self.product}"


class ProductUsage(TranslatableModel, BaseModel):
    """Usage instructions for products"""
    translations = TranslatedFields(
        usage=models.TextField(blank=True, null=True)
    )

    product = models.ForeignKey(
        Product,
        related_name='usage',
        verbose_name=_("Product Usage"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("Product Usage")
        verbose_name_plural = _("Product Usages")

    def __str__(self):
        return f"Usage for {self.product}"


class ProductPackageContentImages(TranslatableModel, BaseModel):
    """Package content images for products"""
    translations = TranslatedFields(
        image=models.ImageField(upload_to='products/package_content/', blank=True, null=True)
    )

    product = models.ForeignKey(
        Product,
        related_name='package_content_images',
        verbose_name=_("Product Package Content Images"),
        on_delete=models.SET_NULL,
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
        on_delete=models.SET_NULL,
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
    
    
# class Certificates(BaseModel):
#     """Company certificates"""
#     image = models.ImageField(upload_to='certificates/', blank=True, null=True)
#     ordering = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ['ordering', 'id']
#         verbose_name = _("Certificate")
#         verbose_name_plural = _("Certificates")

#     def __str__(self):
#         return f"Certificate {self.pk}"

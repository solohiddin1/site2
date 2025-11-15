from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from googletrans import Translator
from django.utils.text import slugify
import uuid

translator = Translator()

def get_unique_code():
    return str(uuid.uuid4().int)[:4]

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True,)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True,)

    class Meta:
        abstract = True


class Category(BaseModel, TranslatableModel):
    # Optionally categories can be translated too; keep a simple name for now.
    translations = TranslatedFields(
        name = models.CharField(max_length=255),
        slug = models.SlugField(
            max_length=255, 
            blank=True, 
            null=True,
            help_text=_("URL-friendly identifier. If left blank, it will be auto-generated from the name."),
            default=None,
            allow_unicode=True
            ),
        )
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or "Category"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        base_lang = 'uz'
        target_langs = ['en', 'ru']

        try:
            base_translation = self.translations.get(language_code=base_lang)
        except Exception as e:
            print(f"⚠️ No base translation found for {base_lang}: {e}")
            return

        # 🔹 Translate only to other languages
        for lang in target_langs:
            try:
                if self.translations.filter(language_code=lang).exists():
                    continue

                translated_name = translator.translate(
                    base_translation.name,
                    src=base_lang,
                    dest=lang
                ).text

                self.create_translation(
                    language_code=lang,
                    name=translated_name,
                    slug=slugify(translated_name, allow_unicode=True),
                )
                print(f"✅ Translated {lang}: {translated_name}")
            except Exception as e:
                print(f"❌ Translation failed for {lang}: {e}")

        # 🔹 Only create slug for Uzbek manually if it doesn't exist
        try:
            uz_translation = self.translations.get(language_code=base_lang)
            if not uz_translation.slug:
                uz_translation.slug = slugify(uz_translation.name, allow_unicode=True)
                uz_translation.save()
        except Exception:
            pass



class Product(TranslatableModel, BaseModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        description=models.TextField(blank=True),
        slug=models.SlugField(
            max_length=255, 
            blank=True, null=True,
            allow_unicode=True),
    )

    unique_code = models.CharField(max_length=50, default=get_unique_code,blank=True, null=True)
    sku = models.CharField(max_length=100, blank=True, null=True, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    def __str__(self):
        return self.safe_translation_getter('name') or 'Unnamed Product'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        base_lang = 'uz'
        target_langs = ['en', 'ru']

        # Set base language slug
        self.set_current_language(base_lang)
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.unique_code}", allow_unicode=True)
            super().save()

        # Get base translation
        try:
            base_translation = self.translations.get(language_code=base_lang)
        except Exception as e:
            print(f"⚠️ No base translation found for {base_lang}: {e}")
            return

        # Translate other languages
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


    # def save(self, *args, **kwargs):
    #     self.set_current_language(base_lang)
    #     if not self.translations__slug:
    #         self.translations__slug = slugify(f"{self.translations__name}-{self.unique_code}", allow_unicode=True)

    #     super().save(*args, **kwargs)

    #     base_lang = 'uz'
    #     target_langs = ['en', 'ru']

    #     self.set_current_language(base_lang)
    #     if not self.translations.get(language_code=base_lang).slug:
    #         self.translations.get(language_code=base_lang).slug = slugify(f"{self.name}-{self.unique_code}", allow_unicode=True)
    #         super().save(update_fields=['slug'])

    #     try:
    #         base_translation = self.translations.get(language_code=base_lang)
    #     except Exception as e:
    #         print(f"⚠️ No base translation found for {base_lang}: {e}")
    #         return

    #     for lang in target_langs:
    #         if self.translations.filter(language_code=lang).exists():
    #             continue

    #         try:
    #             translated_name = translator.translate(base_translation.name, src=base_lang, dest=lang).text
    #             translated_desc = translator.translate(base_translation.description, src=base_lang, dest=lang).text
    #             translated_slug = slugify(f"{translated_name}-{self.unique_code}", allow_unicode=True)

    #             # Safe translation creation
    #             self.create_translation(
    #                 language_code=lang,
    #                 name=translated_name,
    #                 description=translated_desc,
    #                 slug=translated_slug
    #             )

    #             print(f"✅ Translated {lang}: {translated_name}")
    #         except Exception as e:
    #             print(f"❌ Translation failed for {lang}: {e}")


class ProductSpecs(TranslatableModel, BaseModel):
    translations = TranslatedFields(
        specs = models.JSONField(_("Specifications"), encoder=None, decoder=None, blank=True, null=True)
    )
    # key = models.CharField(max_length=255, blank=True, null=True)
    # value = models.CharField(max_length=255, blank=True, null=True)
    product = models.ForeignKey(
        Product, related_name='specs', 
        verbose_name=_("product_specs"), 
        on_delete=models.CASCADE
        )


class ProductImage(BaseModel):
    """
    Multiple images per product.
    Store ordering so admin can control image order. Use an ImageField for uploads.
    """
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    alt = models.CharField(max_length=255, blank=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordering', 'id']

    def __str__(self):
        return f"Image {self.pk} for Product {self.product_id}"


class Certificates(BaseModel):
    """Multiple images per product.

    """
    image = models.ImageField(upload_to='certificates/')
    ordering = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Image"
    

class Company(TranslatableModel, BaseModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        address=models.CharField(max_length=255),
        about_us=models.TextField(),
    )
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    website = models.URLField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return self.safe_translation_getter('name') or "Company"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        base_lang = 'uz'  # default admin input language
        target_langs = ['en', 'ru']

        try:
            base_translation = self.translations.get(language_code=base_lang)
        except Exception as e:
            print(f" No base translation found for {base_lang}: {e}")
            return

        for lang in target_langs:
            try:
                if self.translations.filter(language_code=lang).exists():
                    continue

                translated_name = translator.translate(base_translation.name, src=base_lang, dest=lang).text
                translated_address = translator.translate(base_translation.address, src=base_lang, dest=lang).text
                translated_about = translator.translate(base_translation.about_us, src=base_lang, dest=lang).text

                self.create_translation(
                    language_code=lang,
                    name=translated_name,
                    address=translated_address,
                    about_us=translated_about,
                )
                print(f"Translated {lang}: {translated_name}")
            except Exception as e:
                print(f"Translation failed for {lang}: {e}")


class Partners(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="partners", height_field=None, width_field=None, max_length=None)

    def __str__(self):
        return f"Partner: {self.name}"
    
class ServiceCenterDescription(TranslatableModel):
    """Shared description that changes only with language"""
    translations = TranslatedFields(
        title=models.CharField(max_length=255, blank=True, null=True),
        description=models.TextField()
    )

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True) or "Service Info"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        base_lang = 'uz'  # default admin input language
        target_langs = ['en', 'ru']

        try:
            base_translation = self.translations.get(language_code=base_lang)
        except Exception as e:
            print(f" No base translation found for {base_lang}: {e}")
            return

        for lang in target_langs:
            try:
                if self.translations.filter(language_code=lang).exists():
                    continue

                # If description is empty or None, use original
                to_translate_title = base_translation.title or ""
                to_translate_description = base_translation.description or ""

                if to_translate_title.strip():
                    translated_title = translator.translate(to_translate_title, src=base_lang, dest=lang).text
                else:
                    translated_title = ""

                if to_translate_description.strip():
                    translated_description = translator.translate(to_translate_description, src=base_lang, dest=lang).text
                else:
                    translated_description = ""

                self.create_translation(
                    language_code=lang,
                    title=translated_title,
                    description=translated_description,
                )
                print(f"Translated {lang}: {translated_title} {translated_description}")
            except Exception as e:
                print(f" Translation failed for {lang}: {e}")

class City(models.Model):
    """City choices (Tashkent, Andijan, etc.)"""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    
class ServiceLocation(models.Model):
    """Service center info for each city"""
    city = models.OneToOneField(City, on_delete=models.CASCADE, related_name="service_location")
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    map_url = models.URLField(max_length=2000, blank=True, null=True)  # Google Maps URL
    description = models.ForeignKey(
        ServiceCenterDescription,
        on_delete=models.CASCADE,
        related_name="locations"
    )

    def __str__(self):
        return f"{self.city.name} center"


class Banner(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255, blank=True, null=True),
        image = models.ImageField(upload_to='banners/'),
        alt = models.CharField(max_length=255, blank=True, null=True),
    )
    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or "Banner"

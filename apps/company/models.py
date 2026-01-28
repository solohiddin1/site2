import asyncio
import inspect
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from googletrans import Translator

from apps.categories.models import BaseModel


translator = Translator()


class Company(TranslatableModel, BaseModel):
    """Company information"""
    translations = TranslatedFields(
        name=models.CharField(max_length=255, blank=True, null=True),
        address=models.CharField(max_length=255, blank=True, null=True),
    )
    telegram = models.URLField(max_length=2000, blank=True, null=True)
    instagram = models.URLField(max_length=2000, blank=True, null=True)
    facebook = models.URLField(max_length=2000, blank=True, null=True)
    youtube = models.URLField(max_length=2000, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(max_length=2000, blank=True, null=True)

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or "Company"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        base_lang = 'uz'
        target_langs = ['en', 'ru']

        try:
            base_translation = self.translations.get(language_code=base_lang)
        except Exception as e:
            print(f"⚠️ No base translation found for {base_lang}: {e}")
            return

        for lang in target_langs:
            try:
                if self.translations.filter(language_code=lang).exists():
                    continue

                def translate_field(text):
                    if not text:
                        return ""
                    res = translator.translate(text, src=base_lang, dest=lang)
                    if inspect.isawaitable(res):
                        return asyncio.run(res).text
                    return res.text

                translated_name = translate_field(base_translation.name)
                translated_address = translate_field(base_translation.address)

                self.create_translation(
                    language_code=lang,
                    name=translated_name,
                    address=translated_address,
                )
                print(f"✅ Translated {lang}: {translated_name}")
            except Exception as e:
                print(f"❌ Translation failed for {lang}: {e}")


class Partners(models.Model):
    """Company partners"""
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="partners")

    class Meta:
        verbose_name = _("Partner")
        verbose_name_plural = _("Partners")
        ordering = ['id']

    def __str__(self):
        return f"Partner: {self.name}"


class Banner(TranslatableModel):
    """Homepage banners"""
    translations = TranslatedFields(
        name=models.CharField(max_length=255, blank=True, null=True),
        alt=models.CharField(max_length=255, blank=True, null=True),
        description=models.TextField(blank=True, null=True)
    )
    # image = models.ImageField(upload_to='banners/', blank=True, null=True)
    # image_desktop = models.ImageField(upload_to='banners/desktop/', blank=True, null=True)
    # image_mobile = models.ImageField(upload_to='banners/mobile/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Banner")
        verbose_name_plural = _("Banners")

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or "Banner"


class BannerImages(BaseModel):
    """Additional images for banners"""
    banner = models.ForeignKey(Banner, related_name='additional_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='banners/additional/', blank=True, null=True)
    image_desktop = models.ImageField(upload_to='banners/image_desktop/', blank=True, null=True)
    image_mobile = models.ImageField(upload_to='banners/image_mobile/', blank=True, null=True)
    alt = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _("Banner Image")
        verbose_name_plural = _("Banner Images")
        ordering = ['id']

    def __str__(self):
        return f"Image {self.pk} for Banner {self.banner_id}"


class Connection(BaseModel):
    """Contact form submissions"""
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=50)
    message = models.TextField()

    class Meta:
        verbose_name = _("Connection Request")
        verbose_name_plural = _("Connection Requests")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.phone_number}"

class NewsImage(BaseModel):
    """Images for news articles"""
    news = models.ForeignKey('New', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news/images/', blank=True, null=True)
    alt = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _("News Image")
        verbose_name_plural = _("News Images")
        ordering = ['id']

    def __str__(self):
        return f"Image {self.pk} for News {self.news_id}"
    

class New(BaseModel, TranslatableModel):
    """News model"""
    translations = TranslatedFields(
        title=models.CharField(max_length=255, blank=True, null=True),
        summary=models.TextField(blank=True, null=True),
        description=models.TextField(blank=True, null=True),
        slug = models.SlugField(max_length=255, unique=True, blank=True, null=True),
    )
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    alt = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("News")
        verbose_name_plural = _("News")
        ordering = ['-published_at']
    
    def __str__(self):
        return self.safe_translation_getter('title', any_language=True) or "News"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        base_lang = 'uz'
        target_langs = ['en', 'ru']


        try:
            base_translation = self.translations.get(language_code=base_lang)
        except Exception as e:
            print(f"⚠️ No base translation found for {base_lang}: {e}")
            return

        for lang in target_langs:
            try:
                if self.translations.filter(language_code=lang).exists():
                    continue

                def translate_field(text):
                    if not text:
                        return ""
                    res = translator.translate(text, src=base_lang, dest=lang)
                    if inspect.isawaitable(res):
                        return asyncio.run(res).text
                    return res.text

                translated_title = translate_field(base_translation.title)
                translated_summary = translate_field(base_translation.summary)
                translated_description = translate_field(base_translation.description)

                self.create_translation(
                    language_code=lang,
                    title=translated_title,
                    summary=translated_summary,
                    description=translated_description,
                )
                print(f"✅ Translated {lang}: {translated_title}")

            except Exception as e:
                print(f"❌ Translation failed for {lang}: {e}")
        try:
            if not self.slug:
                base_translation = self.translations.get(language_code=base_lang)
                self.slug = base_translation.title.lower().replace(' ', '-')
                super().save(*args, **kwargs)
            
        except Exception as e:
            print(f"❌ Slug generation failed: {e}")
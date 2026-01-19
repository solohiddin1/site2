import asyncio
import inspect
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from googletrans import Translator
from apps.company.models import BaseModel
from apps.company.middleware import get_logger

translator = Translator()
logger = get_logger()

class Store(BaseModel, TranslatableModel):
    """Store model"""
    translations = TranslatedFields(
        name = models.CharField(max_length=255, blank=True, null=True), 
        address = models.CharField(max_length=255, blank=True, null=True)
    )
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    map_url = models.URLField(max_length=2000, blank=True, null=True)
    
    class Meta:
        verbose_name = _("Store")
        verbose_name_plural = _("Stores")
        ordering = ['id']

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or "Store"

class City(BaseModel):
    """City choices for service locations"""
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        ordering = ['id']

    def __str__(self):
        return self.name


class ServiceCenterDescription(BaseModel, TranslatableModel):
    """Shared description that changes only with language"""
    translations = TranslatedFields(
        title=models.CharField(max_length=255, blank=True, null=True),
        description=models.TextField()
    )

    class Meta:
        verbose_name = _("Service Center Description")
        verbose_name_plural = _("Service Center Descriptions")

    def __str__(self):
        return self.safe_translation_getter('title', any_language=True) or "Service Info"

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

                def get_translated(text):
                    if not text or not text.strip():
                        return ""
                    res = translator.translate(text, src=base_lang, dest=lang)
                    if inspect.isawaitable(res):
                        return asyncio.run(res).text
                    return res.text

                translated_title = get_translated(base_translation.title)
                translated_description = get_translated(base_translation.description)

                self.create_translation(
                    language_code=lang,
                    title=translated_title,
                    description=translated_description,
                )
                logger.info(f"✅ Translated {lang}: {translated_title}")
            except Exception as e:
                logger.error(f"❌ Translation failed for {lang}: {e}")


class ServiceLocation(BaseModel):
    """Service center info for each city"""
    city = models.OneToOneField(City, on_delete=models.CASCADE, related_name="service_location")
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    map_url = models.URLField(max_length=2000, blank=True, null=True)
    description = models.ForeignKey(
        ServiceCenterDescription,
        on_delete=models.CASCADE,
        related_name="locations"
    )

    class Meta:
        verbose_name = _("Service Location")
        verbose_name_plural = _("Service Locations")
        ordering = ['city__name']

    def __str__(self):
        return f"{self.city.name} Service Center"

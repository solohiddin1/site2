from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from googletrans import Translator


translator = Translator()


class City(models.Model):
    """City choices for service locations"""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        ordering = ['name']

    def __str__(self):
        return self.name


class ServiceCenterDescription(TranslatableModel):
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
                print(f"✅ Translated {lang}: {translated_title}")
            except Exception as e:
                print(f"❌ Translation failed for {lang}: {e}")


class ServiceLocation(models.Model):
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

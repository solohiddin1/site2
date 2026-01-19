import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields
from googletrans import Translator
from django.utils.text import slugify
from apps.company.utils import get_unique_code
from apps.company.middleware import get_logger

logger = get_logger()   
translator = Translator()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class Category(BaseModel, TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        unique_code=models.CharField(max_length=50, default=get_unique_code, blank=True, null=True),
        slug=models.SlugField(
            max_length=255,
            blank=True,
            null=True,
            help_text=_("URL-friendly identifier. Auto-generated from name."),
            default=None,
            allow_unicode=True,
        ),
    )
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    second_image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['id']

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or "Category"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        supported_langs = {'uz', 'ru', 'en'}
        
        # 1. Identify source translation
        source_context = None
        try:
             source_context = self.translations.get(language_code='uz')
        except self.translations.model.DoesNotExist:
             source_context = self.translations.first()
        
        if not source_context:
            logger.warning(f"⚠️ No translations found for {self} after save.")
            return

        source_lang = source_context.language_code
        
        # Ensure source fields are populated
        uc = source_context.unique_code or get_unique_code()
        need_save = False
        if not source_context.unique_code:
             source_context.unique_code = uc
             need_save = True
        if not source_context.slug:
             source_context.slug = slugify(f"{source_context.name}-{uc}", allow_unicode=True)
             need_save = True
        
        if need_save:
             source_context.save()

        # 2. Auto-translate
        target_langs = supported_langs - {source_lang}

        for lang in target_langs:
            try:
                if self.translations.filter(language_code=lang).exists():
                    continue

                translated_name = translator.translate(
                    source_context.name,
                    src=source_lang,
                    dest=lang
                ).text
                
                slug_val = slugify(f"{translated_name}-{uc}", allow_unicode=True)

                self.create_translation(
                    language_code=lang,
                    name=translated_name,
                    slug=slug_val,
                    unique_code=uc 
                )
                logger.info(f"✅ Translated {lang}: {translated_name}-{uc}")
            except Exception as e:
                logger.error(f"❌ Translation failed for {lang} (src: {source_lang}): {e}")


class SubCategory(TranslatableModel, BaseModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        unique_code=models.CharField(max_length=50, default=get_unique_code, blank=True, null=True),
        slug=models.SlugField(
            max_length=255,
            blank=True,
            null=True,
            help_text=_("URL-friendly identifier. Auto-generated from name."),
            default=None,
            allow_unicode=True
        ),
    )
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='subcategories/', blank=True, null=True)

    class Meta:
        verbose_name = _("SubCategory")
        verbose_name_plural = _("SubCategories")
        ordering = ['id']

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or "SubCategory"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        supported_langs = {'uz', 'ru', 'en'}
        
        source_context = None
        try:
             source_context = self.translations.get(language_code='uz')
        except self.translations.model.DoesNotExist:
             source_context = self.translations.first()
        
        if not source_context:
            logger.warning(f"⚠️ No translations found for {self} after save.")
            return

        source_lang = source_context.language_code
        uc = source_context.unique_code or get_unique_code()
        
        need_save = False
        if not source_context.unique_code:
             source_context.unique_code = uc
             need_save = True
        if not source_context.slug:
             source_context.slug = slugify(f"{source_context.name}-{uc}", allow_unicode=True)
             need_save = True
        
        if need_save:
             source_context.save()

        target_langs = supported_langs - {source_lang}

        for lang in target_langs:
            try:
                if self.translations.filter(language_code=lang).exists():
                    continue

                translated_name = translator.translate(
                    source_context.name,
                    src=source_lang,
                    dest=lang
                ).text
                
                slug_val = slugify(f"{translated_name}-{uc}", allow_unicode=True)

                self.create_translation(
                    language_code=lang,
                    name=translated_name,
                    slug=slug_val,
                    unique_code=uc 
                )
                logger.info(f"✅ Translated {lang}: {translated_name}-{uc}")
            except Exception as e:
                logger.error(f"❌ Translation failed for {lang} (src: {source_lang}): {e}")

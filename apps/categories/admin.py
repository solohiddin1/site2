from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin
from .models import Category, SubCategory


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ('name', 'id', 'image_thumbnail', 'subcategories_count')
    search_fields = ('translations__name',)
    readonly_fields = ('image_thumbnail', 'second_image_preview')

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return ''
    image_thumbnail.short_description = 'Image Preview'

    def second_image_preview(self, obj):
        if obj.second_image:
            return format_html('<img src="{}" width="100" height="100" />', obj.second_image.url)
        return ''
    second_image_preview.short_description = 'Second Image Preview'

    def subcategories_count(self, obj):
        return obj.subcategories.count()
    subcategories_count.short_description = 'Subcategories'


@admin.register(SubCategory)
class SubCategoryAdmin(TranslatableAdmin):
    list_display = ('name', 'category', 'id', 'image_thumbnail')
    search_fields = ('translations__name', 'category__translations__name')
    list_filter = ('category',)
    readonly_fields = ('image_thumbnail',)

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return ''
    image_thumbnail.short_description = 'Image Preview'

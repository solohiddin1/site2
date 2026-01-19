from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from .models import (
    Product, ProductImage, ProductLongDesc, ProductSpecsTemplate, ProductUsage,
    ProductPackageContentImages, ProductSpecs
)
from django.urls import reverse

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    # fields = ('image', 'alt', 'ordering', 'image_preview', 'image_desktop', 'image_mobile')
    readonly_fields = (
        'image_preview',
        'image_desktop',
        'image_mobile',
        # 'image_thumb_miniatura',
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image Preview'


class ProductSpecsInline(TranslatableTabularInline):
    model = ProductSpecs
    extra = 0


class ProductLongDescInline(TranslatableTabularInline):
    model = ProductLongDesc
    extra = 0
    fields = ('long_desc',)


class ProductUsageInline(TranslatableTabularInline):
    model = ProductUsage
    extra = 0
    fields = ('usage',)


class ProductPackageContentImagesInline(admin.TabularInline):
    model = ProductPackageContentImages
    extra = 0
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image Preview'


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    inlines = [
        ProductImageInline,
        ProductSpecsInline,
        ProductLongDescInline,
        ProductUsageInline,
        ProductPackageContentImagesInline
    ]
    list_display = ('name', 'sku', 'subcategory', 'warranty_months', 'id')
    search_fields = ('translations__name', 'sku', 'unique_code')
    list_filter = ('subcategory', 'subcategory__category')
    readonly_fields = ('unique_code', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('subcategory', 'sku', 'unique_code', 'warranty_months')
        }),
        ('Translations', {
            'fields': ('name', 'description', 'slug')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    # change_form_template = "admin/product/change_form.html"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        try:
            extra_context['add_product_url'] = reverse('products:add_product')
        except Exception:
            extra_context['add_product_url'] = '#'
        return super().changelist_view(request, extra_context=extra_context)



@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image_preview', 'alt', 'ordering')
    list_filter = ('product',)
    readonly_fields = (
        'image_preview',
        'image_desktop',
        'image_mobile',
        # 'image_thumb_miniatura',
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Preview'


@admin.register(ProductSpecsTemplate)
class ProductSpecsTemplateAdmin(TranslatableAdmin):
    list_display = ('name',)
    search_fields = ('translations__name',)
    

# @admin.register(Certificates)
# class CertificatesAdmin(admin.ModelAdmin):
#     list_display = ('id', 'image_preview', 'ordering')
#     readonly_fields = ('image_preview',)

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
#         return "-"
#     image_preview.short_description = 'Preview'

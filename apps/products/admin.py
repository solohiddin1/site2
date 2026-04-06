from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin, TranslatableTabularInline
import mimetypes
from .models import (
    NewArrivals, Product, ProductImage, ProductLongDesc, ProductSpecsTemplate,
    ProductPackageContentImages, ProductSpecs, TopProduct, 
    ProductUsageItem, ProductUsageMediaImage
)
from django.urls import reverse


def _render_file_preview(file_field, width=120):
    """Render admin preview for FileField (image/video/link fallback)."""
    if not file_field:
        return "-"

    try:
        url = file_field.url
    except Exception:
        return "-"

    mime_type, _ = mimetypes.guess_type(str(file_field.name))

    if mime_type and mime_type.startswith("image/"):
        return format_html('<img src="{}" width="{}" style="height:auto;" />', url, width)
    if mime_type and mime_type.startswith("video/"):
        return format_html(
            '<video width="{}" controls preload="metadata"><source src="{}"></video>',
            width,
            url,
        )

    return format_html('<a href="{}" target="_blank">Open file</a>', url)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    # fields = ('image', 'alt', 'ordering', 'image_preview', 'image_desktop')
    readonly_fields = (
        'image_preview',
        'image_desktop',
        # 'image_thumb_miniatura',
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Image Preview'

class ProductUsageItemInline(TranslatableTabularInline):
    model = ProductUsageItem
    extra = 0
    readonly_fields = ('file_preview',)
    # fields = ('media_type', 'file', 'ordering', 'translations__caption')
    fieldsets = (
        ('translations', {
            'fields': ('caption',)
        }),
        ('Usage Item Details', {
            'fields': ('media_type', 'file', 'file_preview', 'external_url', 'ordering')
        }),
    )

    def file_preview(self, obj):
        return _render_file_preview(obj.file)
    file_preview.short_description = 'File Preview'


class ProductUsageMediaImageInline(admin.TabularInline):
    model = ProductUsageMediaImage
    extra = 1
    fields = ('image', 'ordering')

class ProductSpecsInline(TranslatableTabularInline):
    model = ProductSpecs
    extra = 0


class ProductLongDescInline(TranslatableTabularInline):
    model = ProductLongDesc
    extra = 0
    fields = ('long_desc',)


class ProductPackageContentImagesInline(admin.TabularInline):
    model = ProductPackageContentImages
    extra = 1
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
        ProductUsageItemInline,
        ProductLongDescInline,
        ProductPackageContentImagesInline
    ]
    list_display = ('name', 'sku', 'subcategory', 'warranty_months', 'id', 'slug', 'get_image_preview')
    search_fields = ('translations__name', 'sku', 'unique_code')
    list_filter = ('subcategory', 'subcategory__category')
    readonly_fields = ('unique_code', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('subcategory', 'sku', 'unique_code', 'warranty_months', 'slug')
        }),
        ('Translations', {
            'fields': ('name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_image_preview(self, obj):
        first_image = obj.images.first()

        if first_image and first_image.image_desktop:
            return format_html('<img src="{}" width="100" height="100" />', first_image.image_desktop.url)

        if first_image and first_image.image:
            return format_html('<img src="{}" width="100" height="100" />', first_image.image.url)
        return "-"
    get_image_preview.short_description = 'Image Preview'

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
    # list_filter = ('product', 'product__isnull')
    readonly_fields = (
        'image_preview',
        'image_desktop',
    )
    ordering = ('-created_at',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)

        if obj.image_desktop:
            return format_html('<img src="{}" width="100" height="100" />', obj.image_desktop.url)

        return "-"
    image_preview.short_description = 'Preview'


@admin.register(ProductSpecsTemplate)
class ProductSpecsTemplateAdmin(TranslatableAdmin):
    list_display = ('name',)
    search_fields = ('translations__name',)
    

@admin.register(TopProduct)
class TopProductsAdmin(admin.ModelAdmin):
    list_display = ('product', 'ordering', 'created_at', 'get_image_preview')
    list_filter = ('product__subcategory',)
    search_fields = ('product__translations__name', 'product__sku')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('ordering',)
    ordering = ('ordering', '-created_at')
    
    fieldsets = (
        ('Top Product Information', {
            'fields': ('product', 'ordering')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_image_preview(self, obj):
        if not obj.product and not obj.product.images.exists():
            return "-"
        if obj.product.images.exists() and not obj.product.images.first().image_desktop:
            return "-"
        first_image = obj.product.images.first()
        if first_image and first_image.image_desktop:
            return format_html('<img src="{}" width="100" height="100" />', first_image.image_desktop.url)
        return "-"
    get_image_preview.short_description = 'Image Preview'

    
@admin.register(NewArrivals)
class NewArrivalsAdmin(admin.ModelAdmin):
    list_display = ('product', 'ordering', 'created_at')
    list_filter = ('product__subcategory',)
    search_fields = ('product__translations__name', 'product__sku')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('ordering',)
    ordering = ('ordering', '-created_at')
    
    fieldsets = (
        ('New Arrival Information', {
            'fields': ('product', 'ordering')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductUsageItem)
class ProductUsageItemAdmin(TranslatableAdmin):
    inlines = [ProductUsageMediaImageInline]
    list_display = ('product', 'created_at', 'file_preview')
    list_filter = ('product__subcategory',)
    search_fields = ('product__translations__name', 'product__sku')
    readonly_fields = ('created_at', 'updated_at', 'file_preview')
    ordering = ('ordering', '-created_at')
    
    fieldsets = (
        ('Product Usage Item Information', {
            'fields': ('product', 'file', 'file_preview', 'external_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Translations', {
            'fields': ('caption',)
        }),
    )

    def file_preview(self, obj):
        return _render_file_preview(obj.file)
    file_preview.short_description = 'File Preview'

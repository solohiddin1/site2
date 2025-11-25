from django.contrib import admin
from .models import (Product, ProductImage, Category,
                     Certificates, Company, 
                     Partners, ServiceCenterDescription, ServiceLocation, 
                     City, Banner, ProductSpecs, SubCategory,
                     ProductPackageContentImages,
                     ProductLongDesc, ProductUsage)

from parler.admin import TranslatableAdmin, TranslatableTabularInline
from django.utils.html import format_html

class ProductPackageContentImagesInline(admin.TabularInline):
    model = ProductPackageContentImages
    extra = 0
    # don't force the 'image' field here because the model doesn't have a field named 'image'
    readonly_fields = ('image','image_preview',)

    def image_preview(self, obj):
        # try common image field names to avoid AttributeError if 'image' doesn't exist
        image_candidate = None
        for attr in ('image', 'file', 'image_file', 'photo', 'img'):
            image_candidate = getattr(obj, attr, None)
            if image_candidate:
                break
        if image_candidate and hasattr(image_candidate, 'url'):
            return format_html('<img src="{}" width="100" height="100" />', image_candidate.url)
        return "-"
    image_preview.short_description = 'Image Preview'


class ProductUsageInline(TranslatableTabularInline):
    model = ProductUsage
    extra = 0
    fields = ('product', 'usage')


class ProductLongDescInline(TranslatableTabularInline):
    model = ProductLongDesc
    extra = 0
    fields = ('long_desc',)
    # search_fields = ('product', 'translations__long_desc', 'translations__usage')

# @admin.register(ProductLongDesc)
# class ProductLongDescAdmin(admin.ModelAdmin):
#     inlines = [ProductLongDescInline]

# @admin.register(ProductSpecs)
class ProductSpecsInline(TranslatableTabularInline):
    model = ProductSpecs
    extra = 0
    fields = ('specs',)
    # fields = ('city', 'address', 'phone', 'email', 'map_url', 'description')
    # autocomplete_fields = ['city', 'description']  # optional for big lists


@admin.register(Banner)
class BannerAdmin(TranslatableAdmin):
    # model = Banner
    # extra = 3
    list_display = ('name', 'image_preview')
    # fields = ('image', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url)
        return "-"

    image_preview.short_description = "Preview"  # ustun nomi


# Register your models here.
# admin.site.register(Services)

# ---- LOCATION INLINE ----
class ServiceLocationInline(admin.TabularInline):
    model = ServiceLocation
    extra = 0
    fields = ('city', 'address', 'phone', 'email', 'map_url', 'description')
    autocomplete_fields = ['city', 'description']  # optional for big lists

# # ---- CITY ADMIN ----
# @admin.register(City)
# class CityAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     inlines = [ServiceLocationInline]  # Show locations directly in city

# ---- LOCATION ADMIN (optional if you want direct editing) ----
@admin.register(ServiceLocation)
class ServiceLocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'address', 'phone', 'email')
    autocomplete_fields = ['city', 'description']



@admin.register(ServiceCenterDescription)
class ServiceCenterDescriptionAdmin(TranslatableAdmin):
    list_display = ('title',)
    search_fields = ('translations__title',)  # << required for autocomplete
    fieldsets = (
        (None, {
            'fields': ('title', 'description',)
        }),
    )


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)  # << required for autocomplete
    inlines = [ServiceLocationInline]


# @admin.register(ServiceLocation)
# class ServiceLocationAdmin(admin.ModelAdmin):
#     list_display = ('city', 'address', 'phone', 'email')
#     autocomplete_fields = ['city', 'description']



@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display=('name','id',)
    # list_display=('name','id','image_thumbnail')
    search_fields=('translations__name',)
    readonly_fields = ('image_thumbnail',)
    # readonly_fields = ('image',)
    # prepopulated_fields = {'slug': ('name',)}

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
            # return f'<img src="{obj.image.url}" width="50"/>'
        return ''
    # image_thumbnail.allow_tags = True
    image_thumbnail.short_description='Image preview'
    # image_thumbnail.short_description='Image preview'

class ProductInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt', 'ordering', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
            # return f'<img src="{obj.image.url}" width="50"/>'
        return "-"
    image_preview.allow_tags = True
    image_preview.short_description = 'Image Preview'

@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    inlines = [ProductInline, ProductSpecsInline, ProductLongDescInline, ProductUsageInline, ProductPackageContentImagesInline]
    list_display = ('name', 'sku', 'price', 'subcategory', 'id')
    search_fields = ('translations__name', 'sku', 'subcategory__name')
    list_filter = ('subcategory',)
    # prepopulated_fields = {"translations__slug": ("translations__name",)}


@admin.register(SubCategory)
class SubCategoryAdmin(TranslatableAdmin):
    list_display = ('name', 'category', 'id')
    search_fields = ('translations__name', 'category__name')
    list_filter = ('category',)
    # prepopulated_fields = {"translations__slug": ("translations__name",)}

@admin.register(Certificates)
class CertificatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_preview', 'ordering')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "-"
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'


@admin.register(Company)
class CompanyAdmin(TranslatableAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('translations__name',)


@admin.register(Partners)
class PartnersAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50"/>'
        return "-"
    image_preview.allow_tags = True
    image_preview.short_description = 'Logo'

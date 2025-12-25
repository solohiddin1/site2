from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import (Product, ProductImage, Category,
                     Certificates, Company, 
                     Partners, ServiceCenterDescription, ServiceLocation, 
                     City, Banner, ProductSpecs, SubCategory,
                     ProductPackageContentImages,
                     ProductLongDesc, ProductUsage)

from parler.admin import TranslatableAdmin, TranslatableTabularInline

from django import forms
from django_json_widget.widgets import JSONEditorWidget

class ProductSpecsInlineForm(forms.ModelForm):
    class Meta:
        model = ProductSpecs
        fields = "__all__"
        widgets = {
            "specs": JSONEditorWidget,
        }

    def clean_specs(self):
        specs = self.cleaned_data.get("specs", {})
        if not isinstance(specs, dict):
            raise forms.ValidationError("Specs must be a JSON object")
        return specs
    
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
    # fields = ('specs',)
    # form = ProductSpecsInlineForm
    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     if db_field.name == "specs":
    #         kwargs["widget"] = JSONEditorWidget
    #     return super().formfield_for_dbfield(db_field, **kwargs)
    # fields = ("specs",)
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



@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display=('name','id','image_thumbnail')
    search_fields=('translations__name',)
    readonly_fields = ('image_thumbnail', 'second_image_preview')
    # readonly_fields = ('image',)
    # prepopulated_fields = {'slug': ('name',)}

    def image_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
            # return f'<img src="{obj.image.url}" width="50"/>'
        return ''
    # image_thumbnail.allow_tags = True
    image_thumbnail.short_description='Image preview'

    def second_image_preview(self, obj):
        if obj.second_image:
            return format_html('<img src="{}" width="100" height="100" />', obj.second_image.url)
            # return f'<img src="{obj.image.url}" width="50"/>'
        return ''
    second_image_preview.short_description='Second Image Preview'

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
    list_display = ('name', 'sku', 'subcategory', 'id')
    search_fields = ('translations__name', 'sku', 'subcategory__name')
    list_filter = ('subcategory',)
    readonly_fields = ('unique_code',)
    # change_form_template = "admin/product/change_form.html"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['add_product_url'] = reverse('add_product')
        return super().changelist_view(request, extra_context=extra_context)

    # prepopulated_fields = {"translations__slug": ("translations__name",)}


@admin.register(SubCategory)
class SubCategoryAdmin(TranslatableAdmin):
    list_display = ('name', 'category', 'id')
    search_fields = ('translations__name', 'category__name')
    list_filter = ('category',)
    # prepopulated_fields = {"translations__slug": ("translations__name",)}



@admin.register(Company)
class CompanyAdmin(TranslatableAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('translations__name',)


@admin.register(Partners)
class PartnersAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview')
    readonly_fields = ('image_preview',)
    search_fields = ('translations__name',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "-"
    image_preview.allow_tags = True
    image_preview.short_description = 'Logo'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image_preview', 'alt', 'ordering')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "-"
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'


# @admin.register(Certificates)
# class CertificatesAdmin(admin.ModelAdmin):
#     list_display = ('id', 'image_preview', 'ordering')
#     readonly_fields = ('image_preview',)

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
#         return "-"
#     image_preview.allow_tags = True
#     image_preview.short_description = 'Preview'




# Register your models here.
# admin.site.register(Services)

# ---- LOCATION INLINE ----
# class ServiceLocationInline(admin.TabularInline):
#     model = ServiceLocation
#     extra = 0
#     fields = ('city', 'address', 'phone', 'email', 'map_url', 'description')
#     autocomplete_fields = ['city', 'description']  # optional for big lists

# # ---- CITY ADMIN ----
# @admin.register(City)
# class CityAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     inlines = [ServiceLocationInline]  # Show locations directly in city

# ---- LOCATION ADMIN (optional if you want direct editing) ----
# @admin.register(ServiceLocation)
# class ServiceLocationAdmin(admin.ModelAdmin):
#     list_display = ('city', 'address', 'phone', 'email')
#     autocomplete_fields = ['city', 'description']



# @admin.register(ServiceCenterDescription)
# class ServiceCenterDescriptionAdmin(TranslatableAdmin):
#     list_display = ('title',)
#     search_fields = ('translations__title',)  # << required for autocomplete
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'description',)
#         }),
#     )


# @admin.register(City)
# class CityAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     search_fields = ('name',)  # << required for autocomplete
#     inlines = [ServiceLocationInline]


# @admin.register(ServiceLocation)
# class ServiceLocationAdmin(admin.ModelAdmin):
#     list_display = ('city', 'address', 'phone', 'email')
#     autocomplete_fields = ['city', 'description']


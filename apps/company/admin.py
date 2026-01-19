from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin
from .models import Company, Partners, Banner, Connection


@admin.register(Company)
class CompanyAdmin(TranslatableAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('translations__name', 'phone', 'email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'phone', 'email', 'website', 'address')
        }),
        ('Social Media', {
            'fields': ('telegram', 'instagram', 'facebook', 'youtube')
        }),
        # ('About', {
        #     'fields': ('about_us',)
        # }),
        # ('Timestamps', {
        #     'fields': ('created_at', 'updated_at'),
        #     'classes': ('collapse',)
        # }),
    )

    # def logo_preview(self, obj):
    #     if obj.logo:
    #         return format_html('<img src="{}" width="100" height="100" />', obj.logo.url)
    #     return "-"
    # logo_preview.short_description = 'Logo Preview'


@admin.register(Partners)
class PartnersAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview')
    readonly_fields = ('image_preview',)
    search_fields = ('name',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Logo'


@admin.register(Banner)
class BannerAdmin(TranslatableAdmin):
    list_display = ('name', 'is_active', 'image_preview')
    list_filter = ('is_active',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;"/>', obj.image.url)
        return "-"
    image_preview.short_description = "Preview"


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone_number', 'created_at')
    search_fields = ('name', 'phone_number', 'message')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

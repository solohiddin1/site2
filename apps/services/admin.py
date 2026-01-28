from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import City, ServiceLocation, ServiceCenterDescription, Store


# class ServiceLocationInline(admin.TabularInline):
#     model = ServiceLocation
#     extra = 0
#     fields = ('city', 'address', 'phone', 'email', 'map_url', 'description')


# @admin.register(City)
# class CityAdmin(admin.ModelAdmin):
#     list_display = ('name', 'id')
#     search_fields = ('name',)
#     inlines = [ServiceLocationInline]


# @admin.register(ServiceCenterDescription)
# class ServiceCenterDescriptionAdmin(TranslatableAdmin):
#     list_display = ('title', 'id')
#     search_fields = ('translations__title',)
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'description',)
#         }),
#     )


# @admin.register(ServiceLocation)
# class ServiceLocationAdmin(admin.ModelAdmin):
#     list_display = ('city', 'address', 'phone', 'email')
#     list_filter = ('city',)
#     search_fields = ('city__name', 'address', 'phone')
#     fieldsets = (
#         ('Location', {
#             'fields': ('city', 'address', 'map_url')
#         }),
#         ('Contact', {
#             'fields': ('phone', 'email')
#         }),
#         ('Description', {
#             'fields': ('description',)
#         }),
#     )


@admin.register(Store)
class StoreAdmin(TranslatableAdmin):
    list_display = ('id', 'name')
    # search_fields = ('translations__name',)
    # fieldsets = (
    #     (None, {
    #         'fields': ('name', 'address', 'phone', 'email', 'map_url')
    #     }),
    # )

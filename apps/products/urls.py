from django.urls import path
from .views import (
    ProductListView, ProductDetailView, ProductBySubCategoryView,
    ProductImageView, ProductInquiryView, TopProductsView, NewArrivalsView,
    list_products_view, add_product_view, edit_product_view, duplicate_product_view, delete_product_image_view, delete_package_image_view, delete_usage_media_view, delete_usage_media_image_view,
    list_specs_templates_view, add_specs_template_view, edit_specs_template_view, delete_specs_template_view,
    get_specs_template_view, translate_product_fields_view
)

app_name = 'products'

urlpatterns = [
    # Admin product management
    path('admin/products/', list_products_view, name='list_products'),
    path('admin/add_product/', add_product_view, name='add_product'),
    path('admin/edit_product/<int:product_id>/', edit_product_view, name='edit_product'),
    path('admin/duplicate_product/<int:product_id>/', duplicate_product_view, name='duplicate_product'),
    path('admin/delete_image/<int:image_id>/', delete_product_image_view, name='delete_product_image'),
    path('admin/delete_package_image/<int:package_id>/', delete_package_image_view, name='delete_package_image'),
    path('admin/delete_usage_media/<int:usage_id>/', delete_usage_media_view, name='delete_usage_media'),
    path('admin/delete_usage_media_image/<int:image_id>/', delete_usage_media_image_view, name='delete_usage_media_image'),

    # Backward-compatible dashed URL aliases
    path('admin/delete-image/<int:image_id>/', delete_product_image_view, name='delete_product_image_dash'),
    path('admin/delete-package-image/<int:package_id>/', delete_package_image_view, name='delete_package_image_dash'),
    path('admin/delete-usage-media/<int:usage_id>/', delete_usage_media_view, name='delete_usage_media_dash'),
    path('admin/delete-usage-media-image/<int:image_id>/', delete_usage_media_image_view, name='delete_usage_media_image_dash'),
    
    # Specs templates management
    path('admin/specs-templates/', list_specs_templates_view, name='list_specs_templates'),
    path('admin/specs-templates/add/', add_specs_template_view, name='add_specs_template'),
    path('admin/specs-templates/edit/<int:template_id>/', edit_specs_template_view, name='edit_specs_template'),
    path('admin/specs-templates/delete/<int:template_id>/', delete_specs_template_view, name='delete_specs_template'),
    path('admin/specs-templates/get/<int:template_id>/', get_specs_template_view, name='get_specs_template'),
    path('admin/translate-fields/', translate_product_fields_view, name='translate_product_fields'),

    path('', ProductListView.as_view(), name='product-list'),
    path('images/', ProductImageView.as_view(), name='product-images'),
    path('top-products/', TopProductsView.as_view(), name='top-products'),
    path('new-arrivals/', NewArrivalsView.as_view(), name='new-arrivals'),
    path('subcategories/<path:slug>/products/', ProductBySubCategoryView.as_view(), name='subcategory-products'),
    # path('certificates/', CertificatesView.as_view(), name='certificates'),
    path('inquiry/send/', ProductInquiryView.as_view(), name='product-inquiry'),
    path('<path:slug>/', ProductDetailView.as_view(), name='product-detail')
]

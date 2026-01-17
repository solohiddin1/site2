from django.urls import path
from .views import (
    ProductListView, ProductDetailView, ProductBySubCategoryView,
    ProductImageView, CertificatesView,
    list_products_view, add_product_view, edit_product_view, delete_product_image_view, delete_package_image_view
)

app_name = 'products'

urlpatterns = [
    # Admin product management
    path('admin/products/', list_products_view, name='list_products'),
    path('admin/add_product/', add_product_view, name='add_product'),
    path('admin/edit_product/<int:product_id>/', edit_product_view, name='edit_product'),
    path('admin/delete_image/<int:image_id>/', delete_product_image_view, name='delete_product_image'),
    path('admin/delete_package_image/<int:package_id>/', delete_package_image_view, name='delete_package_image'),

    path('', ProductListView.as_view(), name='product-list'),
    path('images/', ProductImageView.as_view(), name='product-images'),
    path('subcategories/<path:slug>/products/', ProductBySubCategoryView.as_view(), name='subcategory-products'),
    path('certificates/', CertificatesView.as_view(), name='certificates'),
    path('<path:slug>/', ProductDetailView.as_view(), name='product-detail'),
]

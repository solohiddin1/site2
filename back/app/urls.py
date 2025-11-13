from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CategoryViewSet, 
    CertificatesViewSet, CompanyViewSet, ProductByCategoryViewSet, ProductView,
    ProductImageView, CategoriesDetailView, PartnersView, NewsDetailView,
    CityViewSet, ServiceLocationViewSet, ServiceCenterDescriptionViewSet, ProductViewSet, ProductDetailView, ProductListView,
    ProductViewSet, BannerView)

router = DefaultRouter()
# router.register(r'languages', LanguageViewSet)
# router.register(r'categories', CategoryViewSet)
# router.register(r'products', ProductViewSet)
# router.register(r'product-translations', ProductTranslationViewSet)
# router.register(r'product-images', ProductImageViewSet)
# router.register(r'certificates', CertificatesViewSet)
# router.register(r'companies', CompanyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('partners/',PartnersView.as_view()),
    # path('products/all/', ProductViewSet.as_view(), name='products-all'),
    # path('products/', ProductByCategoryViewSet.as_view({'get': 'list'}), name='product-images-list'),
    # path('products/<int:pk>/', ProductView.as_view(), name='product-images'),

    path('product-translations/', ProductViewSet.as_view(), name='product-images-list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-images-list'),
    path('products/', ProductListView.as_view(), name='product-images-list'),


    path('product-images/', ProductImageView.as_view(), name='product-detail'),
    path('certificates/', CertificatesViewSet.as_view(), name='certificates'),
    # path('product-translations/', ProductTranslationViewDetail.as_view(), name='product-translation-detail'),
    path('product-images/', ProductImageView.as_view(), name='product-images'),
    # path('languages/', LanguageViewSet.as_view(), name='languages'),
    path('categories/', CategoryViewSet.as_view(), name='categories'),  
    path('companies/', CompanyViewSet.as_view(), name='companies'),
    path('categories/<slug:slug>/', CategoriesDetailView.as_view(), name='categories-detail'),  
    path('news/', NewsDetailView.as_view(), name='news-detail'),
    path('cities/', CityViewSet.as_view(), name='cities'),
    path('service/', ServiceLocationViewSet.as_view(), name='service-locations'),
    # path('service-locations/', ServiceLocationViewSet.as_view(), name='service-locations'),
    path('service-center-descriptions/', ServiceCenterDescriptionViewSet.as_view(), name='service-center-descriptions'),
    path('banner/', BannerView.as_view(),name='banners')
    # path('product-images/', ProductImageViewSet.as_view({'get': 'list'}), name='product-images-list'),
    # path('product-images/<int:pk>/', ProductImageViewSet.as_view({'get': 'retrieve'}), name='product-image-detail'),
    # product-translations

    # path('products/')
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CategoryViewSet, 
    CertificatesViewSet, CompanyViewSet, ProductByCategoryViewSet,
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
    path('banner/', BannerView.as_view(),name='banners'),

    path('certificates/', CertificatesViewSet.as_view(), name='certificates'),

    path('product-translations/', ProductViewSet.as_view(), name='product-images-list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-images-list'),
    path('products/', ProductListView.as_view(), name='product-images-list'),


    path('product-images/', ProductImageView.as_view(), name='product-detail'),
    # path('product-images/', ProductImageView.as_view(), name='product-images'),
    
    path('categories/', CategoryViewSet.as_view(), name='categories'),  
    path('categories/<slug:slug>/', CategoriesDetailView.as_view(), name='categories-detail'),  
    
    path('companies/', CompanyViewSet.as_view(), name='companies'),
    path('news/', NewsDetailView.as_view(), name='news-detail'),
    path('cities/', CityViewSet.as_view(), name='cities'),

    path('service/', ServiceLocationViewSet.as_view(), name='service-locations'),
    path('service-center-descriptions/', ServiceCenterDescriptionViewSet.as_view(), name='service-center-descriptions'),
    # path('service-locations/', ServiceLocationViewSet.as_view(), name='service-locations'),
]
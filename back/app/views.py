from django.shortcuts import render
from rest_framework import viewsets
from .models import Certificates, Category, Product, ProductImage, Company, Partners, ServiceLocation, City, ServiceCenterDescription, Banner
from .serilializers import (
    CitySerializer,
    ServiceLocationSerializer,
    ServiceCenterDescriptionSerializer,
    CategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    CertificatesSerializer,
    CompanySerializer,
    PartnersSerializer,
    BannerSerializer
)
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework import generics 

# Create your views here.

# class CategoryTranslationSerializer(APIView)
class BannerView(APIView):
    def get(self, request, *args, **kwargs):
        lang = request.GET.get('lang', 'en')
        banners = Banner.objects.all().translated(lang)  # 🔥 parler query for language
        data = []
        for b in banners:
            data.append({
                "name": b.safe_translation_getter('name', any_language=True),
                "image": request.build_absolute_uri(b.safe_translation_getter('image').url),
                "alt": b.safe_translation_getter('alt', any_language=True),
            })
        return Response(data)

class CityViewSet(APIView):
    def get(self, request):
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True,context={'request': request})
        return Response(serializer.data)

class ServiceLocationViewSet(APIView):

    def get(self, request):
        service_locations = ServiceLocation.objects.all()
        serializer = ServiceLocationSerializer(service_locations, many=True,context={'request': request})
        return Response(serializer.data)

class ServiceCenterDescriptionViewSet(APIView):
    def get(self, request):
        service_center_descriptions = ServiceCenterDescription.objects.all()
        serializer = ServiceCenterDescriptionSerializer(service_center_descriptions, many=True,context={'request': request})
        return Response(serializer.data)

class PartnersView(APIView):
    def get(self,request):
        partners = Partners.objects.all()
        serializer = PartnersSerializer(partners, many=True)
        return Response(serializer.data)
    

class CertificatesViewSet(APIView):
    def get(self, request):
        certificates = Certificates.objects.all()
        serializer = CertificatesSerializer(certificates, many=True,context={'request': request})
        return Response(serializer.data)

class CompanyViewSet(APIView):
    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)

class CategoryViewSet(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class ProductViewSet(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'translations__slug'

    def get_queryset(self):
        lang = self.request.query_params.get('lang', 'uz')
        return Product.objects.translated(lang, fallback=True)

# class ProductDetailView(generics.RetrieveAPIView):
#     serializer_class = ProductSerializer
#     lookup_field = 'translations__slug'

#     def get_queryset(self):
#         lang = self.request.query_params.get('lang', 'uz')
#         return Product.objects.translated(lang, fallback=True)


class ProductByCategoryViewSet(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    # lookup_field = 'slug'

    def get_queryset(self):
        category_id = self.request.query_params.get('category')  # from ?category=1
        if category_id is not None:
            return Product.objects.filter(category_id=category_id)
        return Product.objects.none()


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category_id = self.request.query_params.get('category')

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset
    
class ProductView(APIView):
    def get(self, request, pk):
        product = Product.objects.filter(pk=pk).first()
        serializer = ProductSerializer(product)

        return Response(serializer.data)


class ProductImageView(APIView):
    def get(self,request):
        product_id = self.request.query_params.get('product')
        images = ProductImage.objects.filter(product_id=product_id)
        print(images)
        serializer = ProductImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)


# class ProductTranslationViewDetail(APIView):
#     def get(self, request):
#         product_id = self.request.query_params.get('product')
#         language_id = self.request.query_params.get('language')
#         product =  None
#         # product =  ProductTranslation.objects.filter(product_id=product_id, language_id=language_id)
#         print(product)
#         print('request entered to product tranlation')
#         if product.exists():
#             print("here1")
#             serializer = ProductTranslationSerializer(product,many=True)
#             return Response(serializer.data)
#         else:
#             print("here2")
#             default_lang = Language.objects.get(is_default=True)
#             print(default_lang)
#             default_product = ProductTranslation.objects.filter(product_id=product_id, language_id=default_lang.id).first()
#             if default_product:
#                 print("entered to default")
#                 serializer = ProductTranslationSerializer(default_product)
#                 return Response(serializer.data)
#         return Response({"detail": " No product translation found"},status=200)


class CategoriesDetailView(APIView):
    def get(self,request,pk):
        data = Category.objects.filter(pk=pk).first()

        serializer = CategorySerializer(data)
        return Response(serializer.data,status=200)


class NewsDetailView(APIView):
    def get(self,request):
        # data = Category.objects.filter(is_news=True)

        # serializer = CategorySerializer(data,many=True)
        return Response(status=200)
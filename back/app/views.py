from django.shortcuts import render
from rest_framework import viewsets
from .models import Certificates, SubCategory, Category, Product, ProductImage, Company, Partners, ServiceLocation, City, ServiceCenterDescription, Banner
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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics 

# Create your views here.

# class CategoryTranslationSerializer(APIView)
class BannerView(APIView):
    def get(self, request, *args, **kwargs):
        lang = request.GET.get('lang', 'en')
        banners = Banner.objects.all().translated(lang)  # parler query for language
        data = []
        for b in banners:
            # Guard against missing image/field
            image_field = b.safe_translation_getter('image', any_language=True)
            image_url = None
            try:
                if image_field and getattr(image_field, 'url', None):
                    image_url = request.build_absolute_uri(image_field.url)
            except Exception:
                image_url = None

            data.append({
                "name": b.safe_translation_getter('name', any_language=True),
                "image": image_url,
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


class ProductViewSet(generics.ListAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'id'

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
    lookup_url_kwarg = 'slug'

    
    def get_queryset(self):
            lang = self.request.query_params.get("lang", "uz")
            return (
                Product.objects.translated(lang)
                .prefetch_related("specs", "images")
                .select_related("subcategory")
            )

    def get_related_products(self):
        product = self.get_object()
        return Product.objects.filter(subcategory=product.subcategory).exclude(id=product.id)[:5]
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['related_products'] = self.get_related_products()
        return context

    
        # return Product.objects.translated(lang, fallback=True)

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
        # Support both category id and category slug filtering.
        category_id = self.request.query_params.get('category')  # from ?category=1
        category_slug = self.request.query_params.get('category_slug')
        lang = self.request.query_params.get('lang', 'uz')

        if category_slug:
            cat = Category.objects.translated(lang, fallback=True).filter(translations__slug=category_slug).first()
            if cat:
                return Product.objects.translated(lang, fallback=True).filter(category_id=cat.id)

            return Product.objects.none()

        if category_id is not None:
            return Product.objects.translated(lang, fallback=True).filter(category_id=category_id)
        return Product.objects.none()


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category_id = self.request.query_params.get('category')
        category_slug = self.request.query_params.get('category_slug')
        lang = self.request.query_params.get('lang', 'uz')

        if category_slug:
            cat = SubCategory.objects.translated(lang, fallback=True).filter(translations__slug=category_slug).first()
            if cat:
                queryset = queryset.filter(subcategory_id=cat.id)
            else:
                queryset = queryset.none()
        elif category_id:
            queryset = queryset.filter(subcategory_id=category_id)

        return queryset
    
# class ProductView(APIView):
#     def get(self, request, pk):
#         product = Product.objects.filter(pk=pk).first()
#         serializer = ProductSerializer(product)

#         return Response(serializer.data)


class ProductImageView(APIView):
    def get(self,request):
        product_id = self.request.query_params.get('product')
        images = ProductImage.objects.filter(product_id=product_id)
        serializer = ProductImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)


class CategoriesDetailView(APIView):
    def get(self, request, slug):
        # Return category by translated slug. Use ?lang= to choose language (default 'uz').
        lang = request.GET.get('lang', 'uz')
        category = Category.objects.translated(lang, fallback=True).filter(translations__slug=slug).first()
        if not category:
            return Response({'detail': 'Not found.'}, status=404)

        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data, status=200)


class NewsDetailView(APIView):
    def get(self,request):
        # data = Category.objects.filter(is_news=True)

        # serializer = CategorySerializer(data,many=True)
        return Response(status=200)
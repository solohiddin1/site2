from django.shortcuts import render
from rest_framework import viewsets
from .models import Certificates, SubCategory, \
    Category, Product, ProductImage, Company,\
    Partners, ServiceLocation, City,\
    ServiceCenterDescription, Banner, Connection
from .serilializers import (
    CitySerializer,
    ServiceLocationSerializer,
    ServiceCenterDescriptionSerializer,
    CategorySerializer,
    SubCategorySerializer,
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
from .utils import send_telegram_message
# Create your views here.

# class CategoryTranslationSerializer(APIView)
class BannerView(APIView):
    def get(self, request, *args, **kwargs):
        lang = request.GET.get('language', 'uz')
        banners = Banner.objects.filter(is_active=True).translated(lang)  # parler query for language
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
                "is_active": b.is_active,
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
    def get(self, request):
        partners = Partners.objects.all().order_by('id')
        serializer = PartnersSerializer(partners, many=True, context={'request': request})
        return Response(serializer.data)
    

class CertificatesViewSet(APIView):
    def get(self, request):
        certificates = Certificates.objects.all()
        serializer = CertificatesSerializer(certificates, many=True,context={'request': request})
        return Response(serializer.data)

class CompanyViewSet(APIView):
    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True, context={'request': request})
        return Response(serializer.data)

class CategoryViewSet(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get(self, request):
        categories = Category.objects.all()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class ProductViewSet(generics.ListAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'id'

    def get(self, request):
        products = Product.objects.all()
        serializer = self.get_serializer(products, many=True)
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


class ProductBySubCategoryView(generics.ListAPIView):
    """List products for a given subcategory.

    Supports:
    - URL path lookup by translated slug (when mounted at /subcategories/<slug:slug>/products/)
    - query param `subcategory_slug` + `lang`
    - query param `subcategory` (numeric id) as fallback
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Support URL param slug (handled by urlconf) or query params
        lang = self.request.query_params.get('lang', 'uz')

        # Prefer URL kwarg 'slug' when available (e.g., /subcategories/<slug>/products/)
        slug = self.kwargs.get('slug')
        if slug:
            # Use language() method to set context, then filter
            subcat = SubCategory.objects.language(lang).filter(translations__slug=slug, translations__language_code=lang).first()
            if subcat:
                return Product.objects.language(lang).filter(subcategory_id=subcat.id)
            return Product.objects.none()

        # Fallback to query params
        subcat_slug = self.request.query_params.get('subcategory_slug')
        subcat_id = self.request.query_params.get('subcategory')

        if subcat_slug:
            subcat = SubCategory.objects.language(lang).filter(translations__slug=subcat_slug, translations__language_code=lang).first()
            if subcat:
                return Product.objects.language(lang).filter(subcategory_id=subcat.id)
            return Product.objects.none()

        if subcat_id:
            return Product.objects.language(lang).filter(subcategory_id=subcat_id)

        # No filter: return all products
        return Product.objects.language(lang).all()


class ProductListView(generics.ListAPIView):
    """List products filtered by subcategory.
    
    Supports:
    - query param `subcategory_slug` + `lang` (recommended)
    - query param `subcategory` (numeric id)
    - query param `category_slug` + `lang` (deprecated, but kept for backward compatibility)
    - query param `category` (deprecated, but kept for backward compatibility)
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        lang = self.request.query_params.get('lang', 'uz')
        
        # New parameter names (recommended)
        subcategory_id = self.request.query_params.get('subcategory')
        subcategory_slug = self.request.query_params.get('subcategory_slug')
        
        # Legacy parameter names (backward compatibility)
        category_id = self.request.query_params.get('category')
        category_slug = self.request.query_params.get('category_slug')

        # Use new params first, fallback to legacy params
        slug_param = subcategory_slug or category_slug
        id_param = subcategory_id or category_id

        if slug_param:
            subcat = SubCategory.objects.language(lang).filter(translations__slug=slug_param, translations__language_code=lang).first()
            if subcat:
                queryset = queryset.filter(subcategory_id=subcat.id)
            else:
                queryset = queryset.none()
        elif id_param:
            queryset = queryset.filter(subcategory_id=id_param)

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
        category = Category.objects.language(lang).filter(translations__slug=slug, translations__language_code=lang).first()
        subcategories = SubCategory.objects.filter(category=category)
        if not category:
            return Response({'detail': 'Not found.'}, status=404)

        serializer = CategorySerializer(category, context={'request': request})
        serializer.subcategories = SubCategorySerializer(subcategories, many=True, context={'request': request}).data
        # print(serializer.data)        
        return Response(serializer.data, status=200)


class NewsDetailView(APIView):
    def get(self,request):
        # data = Category.objects.filter(is_news=True)

        # serializer = CategorySerializer(data,many=True)
        return Response(status=200)

class AboutUsView(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    def get(self,request):
        return Response(status=200)


class ConnectWithUsView(APIView):
    def post(self,request):
        Connection.objects.create(
            name = request.data.get('name'),
            phone_number = request.data.get('phone_number'),
            message = request.data.get('message'),
        )
        send_telegram_message(request.data.get('name'),request.data.get('phone_number'),request.data.get('message'))
        return Response(status=200)

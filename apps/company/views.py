from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import generics
from .models import BannerImages, Company, New, Partners, Banner, Connection
from .serializers import CompanySerializer, PartnersSerializer, BannerSerializer, NewsSerializer
from apps.company.utils import send_telegram_message
from drf_spectacular.utils import extend_schema

class CompanyView(APIView):
    """Get company information"""
    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True, context={'request': request})
        return Response(serializer.data)


class PartnersView(APIView):
    """List all partners"""
    def get(self, request):
        partners = Partners.objects.all().order_by('id')
        serializer = PartnersSerializer(partners, many=True, context={'request': request})
        return Response(serializer.data)



class BannerView(generics.ListAPIView):
    serializer_class = BannerSerializer
    queryset = Banner.objects.filter(is_active=True)
    
    """Get active banners"""
    def get(self, request, *args, **kwargs):
        lang = request.GET.get('language', 'uz')
        # Filter for banners that conform to the requested language
        banners = Banner.objects.filter(is_active=True).language(lang).distinct()
        banner_images = BannerImages.objects.filter(banner__in=banners)

        # data = []
    
        # data.append({
        #     "name": banner.safe_translation_getter('name', language_code=lang),
        #     "image": image_url,
        #     "is_active": banner.is_active,
        #     "alt": banner.safe_translation_getter('alt', language_code=lang),
        # })
        serializer = BannerSerializer(banners, many=True, context={'request': request})
        
        return Response(serializer.data)



# class BannerView(APIView):
#     """Get active banners"""
#     def get(self, request, *args, **kwargs):
#         lang = request.GET.get('language', 'uz')
#         # Filter for banners that conform to the requested language
#         banners = Banner.objects.filter(is_active=True).language(lang).distinct()

#         data = []
#         for banner in banners:
#             # Explicitly get fields for the requested language
#             image_field = banner.safe_translation_getter('image', language_code=lang)
#             image_url = None
#             try:
#                 if image_field and getattr(image_field, 'url', None):
#                     image_url = request.build_absolute_uri(image_field.url)
#             except Exception:
#                 image_url = None

#             data.append({
#                 "name": banner.safe_translation_getter('name', language_code=lang),
#                 "image": image_url,
#                 "is_active": banner.is_active,
#                 "alt": banner.safe_translation_getter('alt', language_code=lang),
#             })
#         return Response(data)


class ConnectWithUsView(APIView):
    """Handle contact form submissions"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        Connection.objects.create(
            name=request.data.get('name'),
            phone_number=request.data.get('phone_number'),
            message=request.data.get('message'),
        )
        name = request.data.get('name')
        phone_number = request.data.get('phone_number')
        message = request.data.get('message')
        
        send_telegram_message(
            name=name,
            phone_number=phone_number,
            message=message
        )
        
        return Response({"success": True}, status=200)

# core/swagger/parameters.py
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, OpenApiExample

ACCEPT_LANGUAGE_HEADER = [
    OpenApiParameter(
        name='Accept-Language',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.HEADER,
        description='Language code (e.g. uz, ru, en)',
        required=False,
        default='uz'
    )
]

class NewsListView(generics.ListAPIView):
    """List all news articles"""
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]
    @extend_schema(
            summary="List News Articles", 
            # parameters=[
            #     {
            #         "name": "language",
            #         "description": "Language code for translations (e.g., 'uz', 'en')",
            #         "required": False,
            #         "type": "string",
            #         "in": "query"
            #     }
            # ],
            parameters=ACCEPT_LANGUAGE_HEADER,
            description="Retrieve a list of all news articles.")
    def get_queryset(self):
        # lang = self.request.query_params.get('language', 'uz')
        lang = self.request.GET.get('language', 'uz')
        return New.objects.filter(is_active=True).language(lang).distinct()

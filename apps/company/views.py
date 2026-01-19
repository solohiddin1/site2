from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Company, Partners, Banner, Connection
from .serializers import CompanySerializer, PartnersSerializer, BannerSerializer
from apps.company.utils import send_telegram_message


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


class BannerView(APIView):
    """Get active banners"""
    def get(self, request, *args, **kwargs):
        lang = request.GET.get('language', 'uz')
        # Filter for banners that conform to the requested language
        banners = Banner.objects.filter(is_active=True).language(lang).distinct()
        data = []
        for banner in banners:
            # Explicitly get fields for the requested language
            image_field = banner.safe_translation_getter('image', language_code=lang)
            image_url = None
            try:
                if image_field and getattr(image_field, 'url', None):
                    image_url = request.build_absolute_uri(image_field.url)
            except Exception:
                image_url = None

            data.append({
                "name": banner.safe_translation_getter('name', language_code=lang),
                "image": image_url,
                "is_active": banner.is_active,
                "alt": banner.safe_translation_getter('alt', language_code=lang),
            })
        return Response(data)


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

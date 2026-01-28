from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField
from .models import BannerImages, Company, NewsImage, Partners, Banner, Connection, New
from apps.categories.serializers import CategoriesWithSubcategoriesSerializer
from apps.categories.models import Category


class CompanySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Company)
    # categories = serializers.SerializerMethodField()

    # def get_categories(self, obj):
    #     qs = Category.objects.all()
    #     return CategoriesWithSubcategoriesSerializer(qs, many=True, context=self.context).data

    name = serializers.CharField(read_only=True)
    address = serializers.CharField(read_only=True)
    about_us = serializers.CharField(read_only=True)

    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'address',
            'about_us',
            'telegram',
            'instagram',
            'facebook',
            'youtube',
            'phone',
            'email',
            'website',
            'translations',
            # 'categories',
        ]


class PartnersSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(source='image')

    class Meta:
        model = Partners
        fields = ['id', 'name', 'logo']


class BannerImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerImages
        fields = '__all__'

class BannerSerializer(serializers.ModelSerializer):
    additional_images = BannerImagesSerializer(many=True, read_only=True)
    translations = TranslatedFieldsField(shared_model=Banner)
    name = serializers.CharField(read_only=True)
    alt = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)

    class Meta:
        model = Banner
        fields = '__all__'


class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = ['id', 'name', 'phone_number', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ['id', 'image', 'alt']
        
class NewsSerializer(serializers.ModelSerializer):
    news_images = serializers.SerializerMethodField()

    class Meta:
        model = New
        fields = ['id', 'title', 'summary', 'description', 'image', 'published_at', 'news_images']
        read_only_fields = ['id', 'title', 'summary', 'published_at']

    def get_news_images(self, obj):
        images = obj.images.all()
        return NewsImageSerializer(images, many=True, context=self.context).data
    
    # def get_news_images(self, obj):
    #     images = obj.images.all()
    #     return [{'id': img.id, 'image_url': img.image.url, 'alt': img.alt} for img in images]

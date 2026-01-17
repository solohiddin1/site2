from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField
from .models import Company, Partners, Banner, Connection
from apps.categories.serializers import CategoriesWithSubcategoriesSerializer
from apps.categories.models import Category


class CompanySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Company)
    categories = serializers.SerializerMethodField()

    def get_categories(self, obj):
        qs = Category.objects.all()
        return CategoriesWithSubcategoriesSerializer(qs, many=True, context=self.context).data

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
            'categories',
        ]


class PartnersSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(source='image')

    class Meta:
        model = Partners
        fields = ['id', 'name', 'logo']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'


class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = ['id', 'name', 'phone_number', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

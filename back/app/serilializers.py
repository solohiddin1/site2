from rest_framework import serializers
from .models import Product, Category, ProductImage, Certificates, Company, Partners, City, ServiceLocation, ServiceCenterDescription, Banner
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Banner
        fields='__all__'

        
# For translated models
class CategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Category)
    class Meta:
        model = Category
        fields = ['id', 'translations', 'image']

class ProductSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Product)
    class Meta:
        model = Product
        fields = ['id', 'translations', 'sku', 'price', 'category']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'alt', 'ordering']

class CertificatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificates
        fields = ['id', 'image', 'ordering']

class CompanySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Company)
    class Meta:
        model = Company
        fields = ['id', 'translations', 'phone', 'email', 'website']

class PartnersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partners
        fields = ['id', 'name', 'image']

class ServiceLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLocation
        fields = ['id', 'city', 'address', 'phone', 'email', 'map_url', 'description']

class CitySerializer(serializers.ModelSerializer):
    # translations = TranslatedFieldsField(shared_model=City)
    
    class Meta:
        model = City
        fields = ['id', 'name',]

class ServiceCenterDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCenterDescription
        fields = ['id', 'title', 'description']
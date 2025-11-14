from rest_framework import serializers
from .models import (Product, Category, ProductImage, Certificates, 
                     Company, Partners, City, ServiceLocation, 
                     ServiceCenterDescription, Banner, 
                     ProductSpecs
                     )
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField


class ProductSpecsSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=ProductSpecs)
    class Meta:
        model = ProductSpecs
        fields = ['id', 'translations', 'product']

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


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'alt', 'ordering']

        
class RelatedProductSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Product)
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'translations', 'sku', 'price', 'category', 'images']  # no related_products


class ProductSerializer(TranslatableModelSerializer):
    # related_products = ProductSerializer(many=True, read_only=True, source='get_related_products')
    related_products = serializers.SerializerMethodField()

    translations = TranslatedFieldsField(shared_model=Product)
    specs = ProductSpecsSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'translations', 'sku', 'price', 'category', 'images', 'specs', 'related_products']

    def get_related_products(self, obj):
        qs = Product.objects.filter(category=obj.category).exclude(id=obj.id)[:4]
        return RelatedProductSerializer(qs, many=True, context=self.context).data
        
        # related_products = obj.get_related_products()
        # serializer = ProductSerializer(related_products, many=True, context=self.context)
        # return serializer.data

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
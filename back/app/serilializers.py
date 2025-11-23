from rest_framework import serializers
from .models import (Product, Category, ProductImage, Certificates, 
                     Company, Partners, City, ServiceLocation, 
                     SubCategory,ProductPackageContentImages,
                     ProductLongDesc,
                     ServiceCenterDescription, Banner, 
                     ProductSpecs, ProductUsage
                     )

from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField

class ProductUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductUsage
        fields = ('id', 'product', 'usage')

class ProductPackageContentImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPackageContentImages
        fields = ['id', 'product_package_content', 'image']

class ProductPackageContentSerializer(serializers.ModelSerializer):
    images = ProductPackageContentImagesSerializer(many=True, read_only=True)
    class Meta:
        model = ProductPackageContentImages
        fields = ['id', 'product_package_content', 'images']

class ProductLongDescSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLongDesc
        fields = ['id', 'product', 'description', 'usage']

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
        fields = ['id', 'translations', 'sku', 'price', 'images']  # no related_products


class SubCategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=SubCategory)
    class Meta:
        model = SubCategory
        fields = ['id', 'translations', 'image']


class ProductSerializer(TranslatableModelSerializer):
    # related_products = ProductSerializer(many=True, read_only=True, source='get_related_products')
    related_products = serializers.SerializerMethodField()
    package_content = ProductPackageContentSerializer(many=True, read_only=True)
    long_desc = ProductLongDescSerializer(many=True, read_only=True)
    translations = TranslatedFieldsField(shared_model=Product)
    specs = ProductSpecsSerializer(many=True, read_only=True)
    usage = ProductUsageSerializer(many=True, read_only=True)
    subcategory = SubCategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'translations', 'sku', 'price', 'images', 
        'specs', 'usage', 'subcategory', 'related_products', 
        'package_content', 'long_desc']

    def get_related_products(self, obj):
        qs = Product.objects.filter(subcategory=obj.subcategory).exclude(id=obj.id)[:4]
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
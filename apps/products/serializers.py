from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField
from .models import (
    Product, ProductImage, ProductLongDesc, 
    ProductPackageContentImages, ProductSpecs, TopProduct, NewArrivals, 
    ProductUsageItem, ProductUsageMediaImage
)
from apps.categories.serializers import SubCategorySerializer


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'alt', 'ordering']


class ProductPackageContentImagesSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = ProductPackageContentImages
        fields = ['id', 'image']


class ProductLongDescSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=ProductLongDesc)

    class Meta:
        model = ProductLongDesc
        fields = ['id', 'product', 'translations']


class ProductSpecsSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=ProductSpecs)

    class Meta:
        model = ProductSpecs
        fields = ['id', 'product', 'translations']


class RelatedProductSerializer(TranslatableModelSerializer):
    """Simplified product serializer for related products"""
    translations = TranslatedFieldsField(shared_model=Product)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'translations', 'slug', 'sku', 'images']

class ProductUsageItemSerializer(serializers.ModelSerializer):
    translations = TranslatedFieldsField(shared_model=ProductUsageItem)
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        return ProductUsageMediaImageSerializer(obj.images.all(), many=True, context=self.context).data

    class Meta:
        model = ProductUsageItem
        fields = ['id', 'media_type', 'file', 'images', 'product', 'ordering', 'external_url', 
                  'translations'
                  ]


class ProductUsageMediaImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductUsageMediaImage
        fields = ['id', 'image', 'ordering']


class ProductSerializer(TranslatableModelSerializer):
    """Full product serializer with all related data"""
    related_products = serializers.SerializerMethodField()
    package_content = serializers.SerializerMethodField()
    long_desc = ProductLongDescSerializer(many=True, read_only=True)
    translations = TranslatedFieldsField(shared_model=Product)
    specs = ProductSpecsSerializer(many=True, read_only=True)
    subcategory = SubCategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    usage_media = ProductUsageItemSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'translations', 'slug', 'sku', 'warranty_months', 'package_content',
            'images', 'specs', 'subcategory',
            'related_products', 'long_desc', 'usage_media'
        ]

    def get_related_products(self, obj):
        qs = Product.objects.filter(subcategory=obj.subcategory).exclude(id=obj.id)[:4]
        return RelatedProductSerializer(qs, many=True, context=self.context).data
        
    def get_package_content(self, obj):
        qs = obj.package_content_images.all()
        return ProductPackageContentImagesSerializer(qs, many=True, context=self.context).data

class TopProductListSerializer(serializers.ModelSerializer):
    """Serializer for listing top products with minimal data"""
    product = RelatedProductSerializer(read_only=True)

    class Meta:
        model = TopProduct
        fields = ['id', 'product', 'ordering']


class NewArrivalsListSerializer(serializers.ModelSerializer):
    """Serializer for listing new arrivals with minimal data"""
    product = RelatedProductSerializer(read_only=True)

    class Meta:
        model = NewArrivals
        fields = ['id', 'product', 'ordering']

    def get_related_products(self, obj):
        qs = Product.objects.filter(subcategory=obj.subcategory).exclude(id=obj.id)[:4]
        return RelatedProductSerializer(qs, many=True, context=self.context).data

    def get_package_content(self, obj):
        qs = obj.package_content_images.all()
        return ProductPackageContentImagesSerializer(qs, many=True, context=self.context).data


# class TopProductsSerializer(ProductSerializer):

#     class Meta:
#         model = TopProduct
#         fields = [
#             'id', 'product'
#             'translations', 'sku', 'warranty_months', 'package_content',
#             'images', 'specs', 'usage', 'subcategory',
#             'related_products', 'long_desc'
#         ]


# class CertificatesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Certificates
#         fields = ['id', 'image', 'ordering']

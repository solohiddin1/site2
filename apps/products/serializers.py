from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField
from .models import (
    Product, ProductImage, ProductLongDesc, ProductUsage,
    ProductPackageContentImages, ProductSpecs, Certificates
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


class ProductUsageSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=ProductUsage)

    class Meta:
        model = ProductUsage
        fields = ('id', 'product', 'translations')


class RelatedProductSerializer(TranslatableModelSerializer):
    """Simplified product serializer for related products"""
    translations = TranslatedFieldsField(shared_model=Product)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'translations', 'sku', 'images']


class ProductSerializer(TranslatableModelSerializer):
    """Full product serializer with all related data"""
    related_products = serializers.SerializerMethodField()
    package_content = serializers.SerializerMethodField()
    long_desc = ProductLongDescSerializer(many=True, read_only=True)
    translations = TranslatedFieldsField(shared_model=Product)
    specs = ProductSpecsSerializer(many=True, read_only=True)
    usage = ProductUsageSerializer(many=True, read_only=True)
    subcategory = SubCategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'translations', 'sku', 'warranty_months', 'package_content',
            'images', 'specs', 'usage', 'subcategory',
            'related_products', 'long_desc'
        ]

    def get_related_products(self, obj):
        qs = Product.objects.filter(subcategory=obj.subcategory).exclude(id=obj.id)[:4]
        return RelatedProductSerializer(qs, many=True, context=self.context).data

    def get_package_content(self, obj):
        qs = obj.package_content_images.all()
        return ProductPackageContentImagesSerializer(qs, many=True, context=self.context).data


class CertificatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificates
        fields = ['id', 'image', 'ordering']

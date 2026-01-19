from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField
from .models import Category, SubCategory
from apps.products.models import Product



class CategorySimpleSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Category)

    class Meta:
        model = Category
        fields = ['id', 'translations', 'slug']


class SubCategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=SubCategory)
    product_count = serializers.SerializerMethodField()
    category = CategorySimpleSerializer(read_only=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'translations', 'image', 'product_count', 'category']

    def get_product_count(self, obj):
        return Product.objects.filter(subcategory=obj).count()


class CategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Category)
    subcategories = serializers.SerializerMethodField()
    subcategories_count = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'translations', 'image', 'second_image', 'subcategories', 'subcategories_count', 'product_count']

    def get_subcategories(self, obj):
        qs = obj.subcategories.all()
        return SubCategorySerializer(qs, many=True, context=self.context).data

    def get_subcategories_count(self, obj):
        return obj.subcategories.all().count()

    def get_product_count(self, obj):
        return Product.objects.filter(subcategory__category=obj).count()


class CategoriesWithSubcategoriesSerializer(TranslatableModelSerializer):
    """Detailed category serializer with subcategories"""
    subcategories = serializers.SerializerMethodField()
    translations = TranslatedFieldsField(shared_model=Category)

    def get_subcategories(self, obj):
        qs = obj.subcategories.all()
        return SubCategorySerializer(qs, many=True, context=self.context).data

    class Meta:
        model = Category
        fields = ['id', 'translations', 'image', 'second_image', 'subcategories']

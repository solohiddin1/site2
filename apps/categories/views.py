from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, SubCategory
from .serializers import CategorySerializer, SubCategorySerializer


class CategoryListView(generics.ListAPIView):
    """List all categories"""
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get(self, request):
        categories = Category.objects.all()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class CategoryDetailView(APIView):
    """Get category details by slug"""
    def get(self, request, slug):
        lang = request.GET.get('lang', 'uz')
        category = Category.objects.language(lang).filter(
            translations__slug=slug,
            translations__language_code=lang
        ).first()

        if not category:
            return Response({'detail': 'Not found.'}, status=404)

        subcategories = SubCategory.objects.filter(category=category)
        serializer = CategorySerializer(category, context={'request': request})
        data = serializer.data
        data['subcategories'] = SubCategorySerializer(
            subcategories,
            many=True,
            context={'request': request}
        ).data

        return Response(data, status=200)


class SubCategoryListView(generics.ListAPIView):
    """List all subcategories"""
    serializer_class = SubCategorySerializer
    queryset = SubCategory.objects.all()

    def get(self, request):
        subcategories = SubCategory.objects.all()
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)

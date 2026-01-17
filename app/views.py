from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework import viewsets, status
from .models import Certificates, SubCategory, \
    Category, Product, ProductImage, Company,\
    Partners, ServiceLocation, City,\
    ServiceCenterDescription, Banner, Connection, \
    ProductLongDesc, ProductUsage, ProductPackageContentImages, ProductSpecs
from .serilializers import (
    CitySerializer,
    ServiceLocationSerializer,
    ServiceCenterDescriptionSerializer,
    CategorySerializer,
    SubCategorySerializer,
    ProductSerializer,
    ProductImageSerializer,
    CertificatesSerializer,
    CompanySerializer,
    PartnersSerializer,
    BannerSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .utils import send_telegram_message
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import uuid
from django.http import JsonResponse

# Create your views here.

# class CategoryTranslationSerializer(APIView)
class BannerView(APIView):
    def get(self, request, *args, **kwargs):
        lang = request.GET.get('language', 'uz')
        banners = Banner.objects.filter(is_active=True).translated(lang)  # parler query for language
        data = []
        for b in banners:
            # Guard against missing image/field
            image_field = b.safe_translation_getter('image', any_language=True)
            image_url = None
            try:
                if image_field and getattr(image_field, 'url', None):
                    image_url = request.build_absolute_uri(image_field.url)
            except Exception:
                image_url = None

            data.append({
                "name": b.safe_translation_getter('name', any_language=True),
                "image": image_url,
                "is_active": b.is_active,
                "alt": b.safe_translation_getter('alt', any_language=True),
            })
        return Response(data)

class CityViewSet(APIView):
    def get(self, request):
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True,context={'request': request})
        return Response(serializer.data)

class ServiceLocationViewSet(APIView):

    def get(self, request):
        service_locations = ServiceLocation.objects.all()
        serializer = ServiceLocationSerializer(service_locations, many=True,context={'request': request})
        return Response(serializer.data)

class ServiceCenterDescriptionViewSet(APIView):
    def get(self, request):
        service_center_descriptions = ServiceCenterDescription.objects.all()
        serializer = ServiceCenterDescriptionSerializer(service_center_descriptions, many=True,context={'request': request})
        return Response(serializer.data)


class PartnersView(APIView):
    def get(self, request):
        partners = Partners.objects.all().order_by('id')
        serializer = PartnersSerializer(partners, many=True, context={'request': request})
        return Response(serializer.data)
    

class CertificatesViewSet(APIView):
    def get(self, request):
        certificates = Certificates.objects.all()
        serializer = CertificatesSerializer(certificates, many=True,context={'request': request})
        return Response(serializer.data)

class CompanyViewSet(APIView):
    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True, context={'request': request})
        return Response(serializer.data)

class CategoryViewSet(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def get(self, request):
        categories = Category.objects.all()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class SubCategoryViewSet(generics.ListAPIView):
    serializer_class = SubCategorySerializer
    queryset = SubCategory.objects.all()

    def get(self, request):
        subcategories = SubCategory.objects.all()
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)


class ProductViewSet(generics.ListAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'id'

    def get(self, request):
        products = Product.objects.all()
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'translations__slug'
    lookup_url_kwarg = 'slug'

    def get_queryset(self):
        lang = self.request.query_params.get("lang", "uz")
        return (
            Product.objects.language(lang)
            .prefetch_related("specs", "images", "package_content_images", "long_desc", "usage")
            .select_related("subcategory")
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        lang = self.request.query_params.get("lang", "uz")
        product = self.get_object()
        context['related_products'] = (
            Product.objects.language(lang)
            .filter(subcategory=product.subcategory)
            .exclude(id=product.id)[:5]
        )
        return context

# class ProductDetailView(generics.RetrieveAPIView):
#     serializer_class = ProductSerializer
#     lookup_field = 'translations__slug'

#     def get_queryset(self):
#         lang = self.request.query_params.get('lang', 'uz')
#         return Product.objects.translated(lang, fallback=True)


class ProductBySubCategoryView(generics.ListAPIView):
    """List products for a given subcategory.

    Supports:
    - URL path lookup by translated slug (when mounted at /subcategories/<slug:slug>/products/)
    - query param `subcategory_slug` + `lang`
    - query param `subcategory` (numeric id) as fallback
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Support URL param slug (handled by urlconf) or query params
        lang = self.request.query_params.get('lang', 'uz')

        # Prefer URL kwarg 'slug' when available (e.g., /subcategories/<slug>/products/)
        slug = self.kwargs.get('slug')
        if slug:
            # Use language() method to set context, then filter
            subcat = SubCategory.objects.language(lang).filter(translations__slug=slug, translations__language_code=lang).first()
            if subcat:
                return Product.objects.language(lang).filter(subcategory_id=subcat.id)
            return Product.objects.none()

        # Fallback to query params
        subcat_slug = self.request.query_params.get('subcategory_slug')
        subcat_id = self.request.query_params.get('subcategory')

        if subcat_slug:
            subcat = SubCategory.objects.language(lang).filter(translations__slug=subcat_slug, translations__language_code=lang).first()
            if subcat:
                return Product.objects.language(lang).filter(subcategory_id=subcat.id)
            return Product.objects.none()

        if subcat_id:
            return Product.objects.language(lang).filter(subcategory_id=subcat_id)

        # No filter: return all products
        return Product.objects.language(lang).all()


class ProductListView(generics.ListAPIView):
    """List products filtered by subcategory.
    
    Supports:
    - query param `subcategory_slug` + `lang` (recommended)
    - query param `subcategory` (numeric id)
    - query param `category_slug` + `lang` (deprecated, but kept for backward compatibility)
    - query param `category` (deprecated, but kept for backward compatibility)
    - query param `search` (search in product name, description, SKU)
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        lang = self.request.query_params.get('lang', 'uz')
        
        # Search functionality
        search_query = self.request.query_params.get('search', '').strip()
        if search_query:
            queryset = queryset.language(lang).filter(
                Q(translations__name__icontains=search_query) |
                Q(translations__description__icontains=search_query) |
                Q(sku__icontains=search_query)
            ).distinct()
            return queryset
        
        # New parameter names (recommended)
        subcategory_id = self.request.query_params.get('subcategory')
        subcategory_slug = self.request.query_params.get('subcategory_slug')
        
        # Legacy parameter names (backward compatibility)
        category_id = self.request.query_params.get('category')
        category_slug = self.request.query_params.get('category_slug')

        # Use new params first, fallback to legacy params
        slug_param = subcategory_slug or category_slug
        id_param = subcategory_id or category_id

        if slug_param:
            subcat = SubCategory.objects.language(lang).filter(translations__slug=slug_param, translations__language_code=lang).first()
            if subcat:
                queryset = queryset.filter(subcategory_id=subcat.id)
            else:
                queryset = queryset.none()
        elif id_param:
            queryset = queryset.filter(subcategory_id=id_param)

        return queryset.language(lang)
    
# class ProductView(APIView):
#     def get(self, request, pk):
#         product = Product.objects.filter(pk=pk).first()
#         serializer = ProductSerializer(product)

#         return Response(serializer.data)


class ProductImageView(APIView):
    def get(self,request):
        product_id = self.request.query_params.get('product')
        images = ProductImage.objects.filter(product_id=product_id)
        serializer = ProductImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)


class CategoriesDetailView(APIView):
    def get(self, request, slug):
        # Return category by translated slug. Use ?lang= to choose language (default 'uz').
        lang = request.GET.get('lang', 'uz')
        category = Category.objects.language(lang).filter(translations__slug=slug, translations__language_code=lang).first()
        subcategories = SubCategory.objects.filter(category=category)
        if not category:
            return Response({'detail': 'Not found.'}, status=404)

        serializer = CategorySerializer(category, context={'request': request})
        serializer.subcategories = SubCategorySerializer(subcategories, many=True, context={'request': request}).data
        # print(serializer.data)        
        return Response(serializer.data, status=200)


class NewsDetailView(APIView):
    def get(self,request):
        # data = Category.objects.filter(is_news=True)

        # serializer = CategorySerializer(data,many=True)
        return Response(status=200)

class AboutUsView(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    def get(self,request):
        return Response(status=200)


class ConnectWithUsView(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        Connection.objects.create(
            name = request.data.get('name'),
            phone_number = request.data.get('phone_number'),
            message = request.data.get('message'),
        )
        name = request.data.get('name')
        phone_number = request.data.get('phone_number')
        message = request.data.get('message')
        send_telegram_message(name=name,
                              phone_number=phone_number,
                              message=message
                              )
        # send_telegram_message(f"Name: {request.data.get('name')}\nPhone: {request.data.get('phone_number')}\nMessage: {request.data.get('message')}")
        return Response({"success": True}, status=200)


@api_view(['POST'])
def create_product(request):
    """
    API endpoint to create a new product with all related data
    Handles: translations, images, specs, long_desc, usage, package images
    """
    try:
        # Extract data from request
        translations_data = {}
        for lang in ['uz', 'en', 'ru']:
            translations_data[lang] = {
                'name': request.data.get(f'translations[{lang}][name]', ''),
                'description': request.data.get(f'translations[{lang}][description]', ''),
            }

        sku = request.data.get('sku', '')
        warranty_months = request.data.get('warranty_months', 12)
        subcategory_id = request.data.get('subcategory')

        if not subcategory_id:
            return Response(
                {"error": "Subcategory is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the product
        product = Product(
            sku=sku,
            warranty_months=int(warranty_months),
            subcategory_id=int(subcategory_id),
            unique_code=str(uuid.uuid4())[:8].upper()
        )

        # Save with translations
        for lang in ['uz', 'en', 'ru']:
            product.set_current_language(lang)
            product.name = translations_data[lang]['name']
            product.description = translations_data[lang]['description']
            product.slug = None  # Will auto-generate
        
        product.save()

        # Handle product images
        images_count = 0
        while f'images[{images_count}]' in request.FILES:
            image_file = request.FILES[f'images[{images_count}]']
            ProductImage.objects.create(
                product=product,
                image=image_file,
                alt=f"{product.name} - Image {images_count + 1}",
                ordering=images_count
            )
            images_count += 1

        # Handle specs (JSON data)
        specs_json = request.data.get('specs')
        if specs_json:
            specs_data = json.loads(specs_json) if isinstance(specs_json, str) else specs_json
            
            product_specs = ProductSpecs(product=product)
            for lang in ['uz', 'en', 'ru']:
                if lang in specs_data and specs_data[lang]:
                    product_specs.set_current_language(lang)
                    product_specs.specs = specs_data[lang]
            product_specs.save()

        # Handle long description
        long_desc_data = {}
        for lang in ['uz', 'en', 'ru']:
            long_desc = request.data.get(f'long_desc[{lang}]', '')
            if long_desc:
                long_desc_data[lang] = long_desc

        if long_desc_data:
            product_long_desc = ProductLongDesc(product=product)
            for lang, text in long_desc_data.items():
                product_long_desc.set_current_language(lang)
                product_long_desc.long_desc = text
            product_long_desc.save()

        # Handle usage
        usage_data = {}
        for lang in ['uz', 'en', 'ru']:
            usage = request.data.get(f'usage[{lang}]', '')
            if usage:
                usage_data[lang] = usage

        if usage_data:
            product_usage = ProductUsage(product=product)
            for lang, text in usage_data.items():
                product_usage.set_current_language(lang)
                product_usage.usage = text
            product_usage.save()

        # Handle package images - create separate objects for each uploaded file
        for lang in ['uz', 'en', 'ru']:
            package_images_key = f'package_images_{lang}'
            if package_images_key in request.FILES:
                files_list = request.FILES.getlist(package_images_key)
                for img_file in files_list:
                    package_img = ProductPackageContentImages(product=product)
                    # Don't use set_current_language, just save the image directly
                    package_img.image = img_file
                    package_img.save()

        # Return success response with product data
        return Response({
            "success": True,
            "message": "Product created successfully",
            "product": {
                "id": product.id,
                "unique_code": product.unique_code,
                "sku": product.sku,
                "name": product.name
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@staff_member_required
def add_product_view(request):
    """
    Template view for adding products - only accessible by admin staff
    """
    if request.method == 'POST':
        try:
            # Extract data from POST request
            translations_data = {}
            for lang in ['uz', 'en', 'ru']:
                translations_data[lang] = {
                    'name': request.POST.get(f'name_{lang}', ''),
                    'description': request.POST.get(f'description_{lang}', ''),
                }

            sku = request.POST.get('sku', '')
            warranty_months = request.POST.get('warranty_months', 12)
            subcategory_id = request.POST.get('subcategory')

            if not subcategory_id:
                messages.error(request, 'Subkategoriya tanlanishi shart!')
                return redirect('add_product')

            # Create the product
            product = Product(
                sku=sku,
                warranty_months=int(warranty_months),
                subcategory_id=int(subcategory_id),
                unique_code=str(uuid.uuid4())[:8].upper()
            )

            # Save with translations and generate slugs for each language
            for lang in ['uz', 'en', 'ru']:
                product.set_current_language(lang)
                product.name = translations_data[lang]['name']
                product.description = translations_data[lang]['description']
                # Generate slug for each language based on the translated name
                if translations_data[lang]['name']:
                    product.slug = slugify(f"{translations_data[lang]['name']}-{product.unique_code}", allow_unicode=True)
                else:
                    product.slug = None
            
            product.save()

            # Handle product images
            images = request.FILES.getlist('images')
            for index, image_file in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=image_file,
                    alt=f"{product.name} - Image {index + 1}",
                    ordering=index
                )

            # Handle specs (JSON data)
            specs_json = request.POST.get('specs')
            if specs_json:
                specs_data = json.loads(specs_json)
                
                product_specs = ProductSpecs(product=product)
                for lang in ['uz', 'en', 'ru']:
                    if lang in specs_data and specs_data[lang]:
                        product_specs.set_current_language(lang)
                        product_specs.specs = specs_data[lang]
                product_specs.save()

            # Handle long description
            long_desc_data = {}
            for lang in ['uz', 'en', 'ru']:
                long_desc = request.POST.get(f'long_desc_{lang}', '')
                if long_desc:
                    long_desc_data[lang] = long_desc

            if long_desc_data:
                product_long_desc = ProductLongDesc(product=product)
                for lang, text in long_desc_data.items():
                    product_long_desc.set_current_language(lang)
                    product_long_desc.long_desc = text
                product_long_desc.save()

            # Handle usage
            usage_data = {}
            for lang in ['uz', 'en', 'ru']:
                usage = request.POST.get(f'usage_{lang}', '')
                if usage:
                    usage_data[lang] = usage

            if usage_data:
                product_usage = ProductUsage(product=product)
                for lang, text in usage_data.items():
                    product_usage.set_current_language(lang)
                    product_usage.usage = text
                product_usage.save()

            # Handle package images - create separate objects for each uploaded file
            for lang in ['uz', 'en', 'ru']:
                package_images_key = f'package_images_{lang}'
                if package_images_key in request.FILES:
                    files_list = request.FILES.getlist(package_images_key)
                    for img_file in files_list:
                        package_img = ProductPackageContentImages(product=product)
                        # Don't use set_current_language, just save the image directly
                        package_img.image = img_file
                        package_img.save()

            messages.success(request, f'Mahsulot muvaffaqiyatli qo\'shildi! (Kod: {product.unique_code})')
            return redirect('admin:app_product_change', product.id)

        except Exception as e:
            messages.error(request, f'Xatolik: {str(e)}')
            return redirect('add_product')

    # GET request - show form
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    
    # Prepare categories with translations
    categories_list = []
    for cat in categories:
        cat.set_current_language('uz')
        categories_list.append({
            'id': cat.id,
            'name': cat.name
        })
    
    # Prepare subcategories JSON for JavaScript
    subcategories_list = []
    for sub in subcategories:
        sub.set_current_language('uz')
        subcategories_list.append({
            'id': sub.id,
            'name': sub.name,
            'category': sub.category_id
        })
    
    context = {
        'categories': categories_list,
        'subcategories_json': json.dumps(subcategories_list)
    }
    
    return render(request, 'add_product.html', context)


@staff_member_required
def list_products_view(request):
    """
    List all products with search and filter - only accessible by admin staff
    """
    products = Product.objects.all().select_related('subcategory').prefetch_related('images')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(translations__name__icontains=search_query) | 
            Q(sku__icontains=search_query) |
            Q(unique_code__icontains=search_query)
        ).distinct()
    
    # Filter by category
    selected_category = request.GET.get('category', '')
    if selected_category:
        products = products.filter(subcategory__category_id=selected_category)
    
    # Set language for display
    products = products.language('uz')
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page', 1)
    products_page = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = Category.objects.all()
    categories_list = []
    for cat in categories:
        cat.set_current_language('uz')
        categories_list.append({
            'id': cat.id,
            'name': cat.name
        })
    
    context = {
        'products': products_page,
        'categories': categories_list,
        'search_query': search_query,
        'selected_category': selected_category
    }
    
    return render(request, 'list_products.html', context)


@staff_member_required
def delete_product_image_view(request, image_id):
    """
    Delete a product image - AJAX endpoint
    """
    if request.method == 'POST':
        try:
            image = get_object_or_404(ProductImage, id=image_id)
            image.delete()
            return JsonResponse({'success': True, 'message': 'Rasm o\'chirildi'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@staff_member_required
def delete_package_image_view(request, package_id):
    """
    Delete a package content image - AJAX endpoint
    """
    if request.method == 'POST':
        try:
            package_img = get_object_or_404(ProductPackageContentImages, id=package_id)
            package_img.delete()
            return JsonResponse({'success': True, 'message': 'Paket rasmi o\'chirildi'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@staff_member_required
def edit_product_view(request, product_id):
    """
    Edit existing product - only accessible by admin staff
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        try:
            # Update translations and regenerate slugs
            for lang in ['uz', 'en', 'ru']:
                product.set_current_language(lang)
                name = request.POST.get(f'name_{lang}', '')
                product.name = name
                product.description = request.POST.get(f'description_{lang}', '')
                # Regenerate slug for each language based on updated name
                if name:
                    product.slug = slugify(f"{name}-{product.unique_code}", allow_unicode=True)
            
            # Update basic fields
            product.sku = request.POST.get('sku', '')
            product.warranty_months = int(request.POST.get('warranty_months', 12))
            product.subcategory_id = int(request.POST.get('subcategory'))
            product.save()

            # Handle new images
            new_images = request.FILES.getlist('images')
            if new_images:
                # Get current max ordering
                max_ordering = product.images.count()
                for index, image_file in enumerate(new_images):
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        alt=f"{product.name} - Image {max_ordering + index + 1}",
                        ordering=max_ordering + index
                    )

            # Update or create specs
            specs_json = request.POST.get('specs')
            if specs_json:
                specs_data = json.loads(specs_json)
                product_specs, created = ProductSpecs.objects.get_or_create(product=product)
                
                for lang in ['uz', 'en', 'ru']:
                    if lang in specs_data and specs_data[lang]:
                        product_specs.set_current_language(lang)
                        product_specs.specs = specs_data[lang]
                product_specs.save()

            # Update or create long description
            for lang in ['uz', 'en', 'ru']:
                long_desc = request.POST.get(f'long_desc_{lang}', '')
                if long_desc:
                    product_long_desc, created = ProductLongDesc.objects.get_or_create(product=product)
                    product_long_desc.set_current_language(lang)
                    product_long_desc.long_desc = long_desc
                    product_long_desc.save()

            # Update or create usage
            for lang in ['uz', 'en', 'ru']:
                usage = request.POST.get(f'usage_{lang}', '')
                if usage:
                    product_usage, created = ProductUsage.objects.get_or_create(product=product)
                    product_usage.set_current_language(lang)
                    product_usage.usage = usage
                    product_usage.save()

            # Handle package images - create separate objects for each uploaded file
            for lang in ['uz', 'en', 'ru']:
                package_images_key = f'package_images_{lang}'
                if package_images_key in request.FILES:
                    files_list = request.FILES.getlist(package_images_key)
                    for img_file in files_list:
                        package_img = ProductPackageContentImages(product=product)
                        # Don't use set_current_language, just save the image directly
                        package_img.image = img_file
                        package_img.save()

            messages.success(request, 'Mahsulot muvaffaqiyatli yangilandi!')
            return redirect('edit_product', product_id=product.id)

        except Exception as e:
            messages.error(request, f'Xatolik: {str(e)}')
            return redirect('edit_product', product_id=product.id)

    # GET request - show form with existing data
    product.set_current_language('uz')
    product_uz = {'name': product.name, 'description': product.description}
    product.set_current_language('en')
    product_en = {'name': product.name, 'description': product.description}
    product.set_current_language('ru')
    product_ru = {'name': product.name, 'description': product.description}
    
    # Get long descriptions
    long_desc = {'uz': '', 'en': '', 'ru': ''}
    try:
        product_long_desc = ProductLongDesc.objects.get(product=product)
        for lang in ['uz', 'en', 'ru']:
            product_long_desc.set_current_language(lang)
            long_desc[lang] = product_long_desc.long_desc
    except ProductLongDesc.DoesNotExist:
        pass
    
    # Get usage
    usage = {'uz': '', 'en': '', 'ru': ''}
    try:
        product_usage = ProductUsage.objects.get(product=product)
        for lang in ['uz', 'en', 'ru']:
            product_usage.set_current_language(lang)
            usage[lang] = product_usage.usage
    except ProductUsage.DoesNotExist:
        pass
    
    # Get specs
    specs = {'uz': {}, 'en': {}, 'ru': {}}
    try:
        product_specs = ProductSpecs.objects.get(product=product)
        for lang in ['uz', 'en', 'ru']:
            product_specs.set_current_language(lang)
            specs[lang] = product_specs.specs if product_specs.specs else {}
    except ProductSpecs.DoesNotExist:
        pass
    
    # Get categories and subcategories
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    
    categories_list = []
    for cat in categories:
        cat.set_current_language('uz')
        categories_list.append({
            'id': cat.id,
            'name': cat.name
        })
    
    subcategories_list = []
    for sub in subcategories:
        sub.set_current_language('uz')
        subcategories_list.append({
            'id': sub.id,
            'name': sub.name,
            'category': sub.category_id
        })
    
    context = {
        'product': product,
        'product_uz': product_uz,
        'product_en': product_en,
        'product_ru': product_ru,
        'long_desc': long_desc,
        'usage': usage,
        'specs': specs,
        'categories': categories_list,
        'subcategories_json': json.dumps(subcategories_list),
        'is_edit': True
    }
    
    return render(request, 'edit_product.html', context)
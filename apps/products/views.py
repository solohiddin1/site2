from django.db.models import Q
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from .models import (Product, ProductImage, ProductLongDesc, 
                     ProductPackageContentImages, ProductUsage, 
                     ProductSpecs, ProductSpecsTemplate, TopProduct)
from .utils import send_product_inquiry_telegram
from apps.company.models import Connection
from .serializers import ProductSerializer, ProductImageSerializer
from apps.categories.models import SubCategory
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from apps.categories.models import Category
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.text import slugify
from django.http import JsonResponse
from django.conf import settings
import uuid
import json


class ProductListView(generics.ListAPIView):
    """
    List products filtered by subcategory.
    
    Supports:
    - query param `subcategory_slug` + `lang` (recommended)
    - query param `subcategory` (numeric id)
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
        
        # Filter by subcategory
        subcategory_id = self.request.query_params.get('subcategory')
        subcategory_slug = self.request.query_params.get('subcategory_slug')

        if subcategory_slug:
            subcat = SubCategory.objects.language(lang).filter(
                translations__slug=subcategory_slug,
                translations__language_code=lang
            ).first()
            if subcat:
                queryset = queryset.filter(subcategory_id=subcat.id)
            else:
                queryset = queryset.none()
        elif subcategory_id:
            queryset = queryset.filter(subcategory_id=subcategory_id)

        return queryset.language(lang)


class ProductDetailView(generics.RetrieveAPIView):
    """Get product details by slug"""
    serializer_class = ProductSerializer
    lookup_field = 'translations__slug'
    lookup_url_kwarg = 'slug'

    def get_queryset(self):
        lang = self.request.query_params.get("lang", "uz")
        slug = self.kwargs.get('slug')
        
        # Filter by both slug AND language_code to avoid MultipleObjectsReturned error
        return (
            Product.objects.language(lang)
            .filter(translations__slug=slug, translations__language_code=lang)
            .prefetch_related("specs", "images", "package_content_images", "long_desc", "usage")
            .select_related("subcategory")
            .distinct()
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


class ProductBySubCategoryView(generics.ListAPIView):
    """
    List products for a given subcategory.

    Supports:
    - URL path lookup by translated slug (when mounted at /subcategories/<slug:slug>/products/)
    - query param `subcategory_slug` + `lang`
    - query param `subcategory` (numeric id) as fallback
    """
    serializer_class = ProductSerializer

    def get_queryset(self):
        lang = self.request.query_params.get('lang', 'uz')
        # translation.activate(lang)
        # Prefer URL kwarg 'slug' when available
        slug = self.kwargs.get('slug')
        
        if slug:
            # translation.activate(lang)
            # translation.set_current_language(lang)
            subcat = SubCategory.objects.language(lang).filter(
                translations__slug=slug,
                translations__language_code=lang
            ).first()
            # subcat = SubCategory.objects.language(lang).filter(
            #     translations__slug=slug,
            #     translations__language_code=lang
            # ).first()
            if subcat:
                products = Product.objects.language(lang).filter(subcategory_id=subcat.id)
                return products
            return Product.objects.none()

        # Fallback to query params
        subcat_slug = self.request.query_params.get('subcategory_slug')
        subcat_id = self.request.query_params.get('subcategory')

        if subcat_slug:
            subcat = SubCategory.objects.language(lang).filter(
                translations__slug=subcat_slug,
                translations__language_code=lang
            ).first()
            if subcat:
                products = Product.objects.language(lang).filter(subcategory_id=subcat.id)
                return products
            return Product.objects.none()

        if subcat_id:
            products = Product.objects.language(lang).filter(subcategory_id=subcat_id)
            return products

        # No filter: return all products
        return Product.objects.language(lang).all()


class ProductImageView(APIView):
    """Get images for a specific product"""
    def get(self, request):
        product_id = self.request.query_params.get('product')
        images = ProductImage.objects.filter(product_id=product_id)
        serializer = ProductImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)


class TopProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        lang = self.request.query_params.get('lang', 'uz')
        
        # Get all products that are marked as top products
        top_product_list = TopProduct.objects.first()
        if top_product_list:
            return top_product_list.products.language(lang).all()
        return Product.objects.none()

class ProductInquiryView(generics.CreateAPIView):
    """Handle product inquiry form submissions"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        product_id = request.data.get('product_id')
        name = request.data.get('name')
        phone_number = request.data.get('phone_number')
        message = request.data.get('message')
        
        product_data = None
        if product_id:
            try:
                # Get product info for telegram message
                product = Product.objects.get(id=product_id)
                # Ensure we get name/slug in a consistent language (uz)
                product.set_current_language('uz')
                
                # Try to construct a link if we have request context
                product_url = f"/products/{product.slug}"
                if hasattr(request, 'build_absolute_uri'):
                    # This might be tricky if frontend is on different domain
                    # But often the backend knows the frontend domain
                    pass
                
                product_data = {
                    'name': product.name,
                    'sku': product.sku,
                    'url': f"{settings.BASE_URL}/uz{product_url}" # Placeholder domain
                }
            except Product.DoesNotExist:
                pass
        
        # Send Telegram message
        response = send_product_inquiry_telegram(
            name=name,
            phone_number=phone_number,
            message=message,
            product_data=product_data
        )
        
        # Save to database
        Connection.objects.create(
            name=name,
            phone_number=phone_number,
            message=f"[MAHSULOT SO'ROVI: {product_data['name'] if product_data else 'ID:'+str(product_id)}] {message}"
        )
        print(f"Telegram response status: {response.status_code}, response text: {response.text}")
        return Response({"success": True}, status=200)


# class CertificatesView(APIView):
#     """List all certificates"""
#     def get(self, request):
#         certificates = Certificates.objects.all()
#         serializer = CertificatesSerializer(certificates, many=True, context={'request': request})
#         return Response(serializer.data)



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
                return redirect('products:add_product')

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
            return redirect('products:edit_product', product_id=product.id)

        except Exception as e:
            messages.error(request, f'Xatolik: {str(e)}')
            return redirect('products:add_product')

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
    
    # Get specs templates
    specs_templates = ProductSpecsTemplate.objects.all().order_by('translations__name')
    templates_list = []
    for tmpl in specs_templates:
        tmpl.set_current_language('uz')
        templates_list.append({
            'id': tmpl.id,
            'name': tmpl.name or 'Unnamed'
        })
    
    context = {
        'categories': categories_list,
        'subcategories_json': json.dumps(subcategories_list),
        'specs_templates': templates_list
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
            return redirect('products:edit_product', product_id=product.id)

        except Exception as e:
            messages.error(request, f'Xatolik: {str(e)}')
            return redirect('products:edit_product', product_id=product.id)

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
    
    # Get specs templates
    specs_templates = ProductSpecsTemplate.objects.all().order_by('translations__name')
    templates_list = []
    for tmpl in specs_templates:
        tmpl.set_current_language('uz')
        templates_list.append({
            'id': tmpl.id,
            'name': tmpl.name or 'Unnamed'
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
        'specs_templates': templates_list,
        'is_edit': True
    }
    
    return render(request, 'edit_product.html', context)


# ===================== SPECS TEMPLATES VIEWS =====================

@staff_member_required
def list_specs_templates_view(request):
    """List all specs templates"""
    templates = ProductSpecsTemplate.objects.all().order_by('-created_at')
    
    # Set language for display
    for template in templates:
        template.set_current_language('uz')
    
    context = {
        'templates': templates
    }
    
    return render(request, 'list_specs_templates.html', context)


@staff_member_required
def add_specs_template_view(request):
    """Add new specs template"""
    if request.method == 'POST':
        try:
            # Get template name for each language
            name_uz = request.POST.get('name_uz', '').strip()
            name_en = request.POST.get('name_en', '').strip()
            name_ru = request.POST.get('name_ru', '').strip()
            
            if not name_uz:
                messages.error(request, "O'zbekcha nom kiritilishi shart!")
                return redirect('products:add_specs_template')
            
            # Parse specs JSON for each language
            specs_json = request.POST.get('specs_json', '{}')
            specs_data = json.loads(specs_json)
            
            # Create template
            template = ProductSpecsTemplate()
            
            # Save for each language
            for lang, name in [('uz', name_uz), ('en', name_en), ('ru', name_ru)]:
                template.set_current_language(lang)
                template.name = name
                template.specs = specs_data.get(lang, {})
            
            template.save()
            
            messages.success(request, f"Shablon muvaffaqiyatli qo'shildi!")
            return redirect('products:list_specs_templates')
            
        except Exception as e:
            messages.error(request, f'Xatolik: {str(e)}')
            return redirect('products:add_specs_template')
    
    return render(request, 'add_specs_template.html')


@staff_member_required
def edit_specs_template_view(request, template_id):
    """Edit existing specs template"""
    template = get_object_or_404(ProductSpecsTemplate, id=template_id)
    
    if request.method == 'POST':
        try:
            # Update names
            name_uz = request.POST.get('name_uz', '').strip()
            name_en = request.POST.get('name_en', '').strip()
            name_ru = request.POST.get('name_ru', '').strip()
            
            if not name_uz:
                messages.error(request, "O'zbekcha nom kiritilishi shart!")
                return redirect('products:edit_specs_template', template_id=template_id)
            
            # Parse specs JSON
            specs_json = request.POST.get('specs_json', '{}')
            specs_data = json.loads(specs_json)
            
            # Update for each language
            for lang, name in [('uz', name_uz), ('en', name_en), ('ru', name_ru)]:
                template.set_current_language(lang)
                template.name = name
                template.specs = specs_data.get(lang, {})
            
            template.save()
            
            messages.success(request, "Shablon muvaffaqiyatli yangilandi!")
            return redirect('products:list_specs_templates')
            
        except Exception as e:
            messages.error(request, f'Xatolik: {str(e)}')
            return redirect('products:edit_specs_template', template_id=template_id)
    
    # Prepare template data for editing
    template_uz = {}
    template_en = {}
    template_ru = {}
    
    template.set_current_language('uz')
    template_uz = {
        'name': template.name or '',
        'specs': template.specs or {}
    }
    
    template.set_current_language('en')
    template_en = {
        'name': template.name or '',
        'specs': template.specs or {}
    }
    
    template.set_current_language('ru')
    template_ru = {
        'name': template.name or '',
        'specs': template.specs or {}
    }
    
    # Combine specs for JavaScript
    specs = {
        'uz': template_uz['specs'],
        'en': template_en['specs'],
        'ru': template_ru['specs']
    }
    
    context = {
        'template': template,
        'template_uz': template_uz,
        'template_en': template_en,
        'template_ru': template_ru,
        'specs': json.dumps(specs),
        'is_edit': True
    }
    
    return render(request, 'edit_specs_template.html', context)


@staff_member_required
def delete_specs_template_view(request, template_id):
    """Delete specs template"""
    if request.method == 'POST':
        try:
            template = get_object_or_404(ProductSpecsTemplate, id=template_id)
            template.delete()
            return JsonResponse({'success': True, 'message': "Shablon o'chirildi"})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@staff_member_required
def get_specs_template_view(request, template_id):
    """Get specs template data (AJAX endpoint)"""
    try:
        template = get_object_or_404(ProductSpecsTemplate, id=template_id)
        
        specs_data = {}
        for lang in ['uz', 'en', 'ru']:
            template.set_current_language(lang)
            specs_data[lang] = template.specs or {}
        
        return JsonResponse({
            'success': True,
            'specs': specs_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
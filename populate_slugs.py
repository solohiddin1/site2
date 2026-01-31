
import os
import django
import sys

# Setup Django environment
sys.path.append('/home/solohiddin/files/folder/site2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from apps.categories.models import Category, SubCategory
from apps.products.models import Product

def populate_slugs():
    print("Populating Category slugs...")
    for cat in Category.objects.all():
        print(f"Processing Category {cat.id}: {cat.safe_translation_getter('name', any_language=True)}")
        # The save method has the logic to generate slug if missing
        cat.save()
        print(f"  -> Slug: {cat.slug}")

    print("\nPopulating SubCategory slugs...")
    for sub in SubCategory.objects.all():
        print(f"Processing SubCategory {sub.id}: {sub.safe_translation_getter('name', any_language=True)}")
        # The save method has the logic to generate slug if missing
        sub.save()
        print(f"  -> Slug: {sub.slug}")

    print("\nPopulating Product slugs...")
    for prod in Product.objects.all():
        print(f"Processing Product {prod.id}: {prod.safe_translation_getter('name', any_language=True)}")
        # The save method has the logic to generate slug if missing
        prod.save()
        print(f"  -> Slug: {prod.slug}")

if __name__ == '__main__':
    populate_slugs()

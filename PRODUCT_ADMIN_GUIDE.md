# Product Admin Interface Guide

## Overview
A user-friendly interface to add products with multi-language support (Uzbek, English, Russian) without manually editing JSON files.

## Features
✅ **Multi-language tabs** - Separate forms for Uzbek, English, and Russian
✅ **User-friendly specs builder** - Add technical specifications as key-value pairs (no JSON editing needed)
✅ **Image upload** - Upload multiple product images with preview
✅ **Package content images** - Upload separate package images for each language
✅ **Rich text fields** - Full description, usage instructions, warranty info
✅ **Category/Subcategory selection** - Dropdown menus with dynamic filtering
✅ **Real-time validation** - Required fields marked with asterisk (*)

## How to Access
Navigate to: `http://localhost:5173/uz/add-product` (or `/en/add-product`, `/ru/add-product`)

## Form Structure

### Language Tabs (O'zbekcha / English / Русский)
Each language tab contains:

1. **Product Name*** (Required)
   - Enter the product name in that language
   - Example: "Suv isitkichi" (UZ), "Water Heater" (EN), "Водонагреватель" (RU)

2. **Short Description**
   - Brief product summary
   - Displayed in product cards and listings

3. **Full Description**
   - Detailed product information
   - Displayed on product detail page

4. **Usage Instructions**
   - How to use the product
   - Safety guidelines, operation instructions

5. **Technical Specifications**
   - Click "+ Xususiyat qo'shish" to add specs
   - Each spec has:
     - **Key**: Specification name (e.g., "Quvvat", "Power", "Мощность")
     - **Value**: Specification value (e.g., "1500W")
   - Click trash icon to remove a spec
   - Add as many specs as needed

6. **Package Content Image**
   - Upload an image showing what's included in the package
   - Different image for each language if needed

### Common Fields (Umumiy ma'lumotlar)

1. **SKU (Artikul)**
   - Stock Keeping Unit / Article number
   - Optional but recommended for inventory management

2. **Warranty (Kafolat)**
   - Number of months
   - Default: 12 months

3. **Category*** (Required)
   - Select main product category
   - Subcategories will be filtered based on this

4. **Subcategory*** (Required)
   - Select specific subcategory
   - Only shows subcategories of selected category

5. **Product Images**
   - Upload multiple product photos
   - Click "Choose files" to select
   - Preview shows uploaded images
   - Click trash icon to remove

## Step-by-Step Guide

### 1. Fill Uzbek Information
- Switch to "O'zbekcha" tab
- Enter product name (required)
- Add description, full description, usage
- Add technical specs:
  - Example: Key: "Quvvat", Value: "1500W"
  - Example: Key: "Hajm", Value: "50L"
- Upload package content image if needed

### 2. Fill English Information
- Switch to "English" tab
- Enter product name (required)
- Add description, full description, usage
- Add technical specs in English:
  - Example: Key: "Power", Value: "1500W"
  - Example: Key: "Capacity", Value: "50L"
- Upload package content image if needed

### 3. Fill Russian Information
- Switch to "Русский" tab
- Enter product name (required)
- Add description, full description, usage
- Add technical specs in Russian:
  - Example: Key: "Мощность", Value: "1500W"
  - Example: Key: "Объем", Value: "50L"
- Upload package content image if needed

### 4. Fill Common Fields
- Add SKU (optional)
- Set warranty period
- Select category
- Select subcategory (appears after category selection)
- Upload product images (multiple allowed)

### 5. Submit
- Click "Saqlash" (Save) button
- Wait for success message
- Product will be created with unique code

## API Endpoint

### POST `/api/products/create/`

**Request Format**: `multipart/form-data`

**Fields**:
```
translations[uz][name]: string (required)
translations[en][name]: string (required)
translations[ru][name]: string (required)
translations[uz][description]: string
translations[en][description]: string
translations[ru][description]: string
sku: string
warranty_months: number (default: 12)
subcategory: number (required)
images[0]: file
images[1]: file
images[...]: file
specs: JSON string
  {
    "uz": {"Key1": "Value1", "Key2": "Value2"},
    "en": {"Key1": "Value1", "Key2": "Value2"},
    "ru": {"Key1": "Value1", "Key2": "Value2"}
  }
long_desc[uz]: string
long_desc[en]: string
long_desc[ru]: string
usage[uz]: string
usage[en]: string
usage[ru]: string
package_image_uz: file
package_image_en: file
package_image_ru: file
```

**Success Response**:
```json
{
  "success": true,
  "message": "Product created successfully",
  "product": {
    "id": 123,
    "unique_code": "A1B2C3D4",
    "sku": "WH-1500",
    "name": "Suv isitkichi"
  }
}
```

**Error Response**:
```json
{
  "error": "Subcategory is required"
}
```

## Database Structure

When you submit the form, the following records are created:

1. **Product** - Main product record with translations (name, description, slug)
2. **ProductImage** - Multiple records for each uploaded image
3. **ProductSpecs** - Technical specifications in JSON format for all languages
4. **ProductLongDesc** - Full description in all languages
5. **ProductUsage** - Usage instructions in all languages
6. **ProductPackageContentImages** - Package images for each language

All translations are stored using `django-parler` for proper multi-language support.

## Tips & Best Practices

1. **Always fill all 3 languages** - This ensures the product displays correctly in all language versions of the site

2. **Use descriptive spec keys** - Clear specification names help users understand the product
   - Good: "Quvvat" / "Power" / "Мощность"
   - Bad: "Q" / "P" / "М"

3. **Upload high-quality images** - Product images should be:
   - Clear and well-lit
   - At least 800x800 pixels
   - Show product from multiple angles
   - First image becomes the main/featured image

4. **Keep descriptions consistent** - Information should match across all languages

5. **Use warranty months accurately** - Standard warranties: 12, 24, 36, 60 months

6. **Fill package content images** - Helps customers understand what's included

7. **SKU naming convention** - Use a consistent format:
   - Category code + Product code
   - Example: "WH-1500" (Water Heater 1500W)

## Troubleshooting

**Q: Subcategory dropdown is empty**
- Make sure you selected a category first
- Only subcategories belonging to selected category will show

**Q: Image preview not showing**
- Check file format (should be image/jpeg, image/png, etc.)
- Check file size (should be < 5MB)

**Q: Form not submitting**
- Check all required fields (marked with *)
- Must fill product name in all 3 languages
- Must select category and subcategory

**Q: Specs not saving**
- Make sure both Key and Value are filled
- Empty specs (where key or value is blank) are automatically ignored

**Q: Success message not appearing**
- Check browser console for errors
- Verify Django backend is running on port 8000
- Check CORS settings in Django

## Technical Notes

- Frontend: React + TypeScript + Tailwind CSS
- Backend: Django 5.2.7 + django-parler
- Form uses multipart/form-data for file uploads
- Specs are converted from key-value pairs to JSON automatically
- Product slug is auto-generated from name
- Unique code is auto-generated (8 characters)
- Images are stored in `media/products/` directory

## Future Enhancements

Potential improvements:
- Drag-and-drop image reordering
- Rich text editor for descriptions
- Auto-translation between languages
- Bulk product import from CSV/Excel
- Product duplication feature
- Image cropping/editing tools
- SEO metadata fields

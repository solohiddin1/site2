# Frontend API Brief & AI Prompt

This document explains the backend API endpoints available in this Django project and includes a ready-to-use prompt for an AI/frontend developer to build the frontend.

Base URL: http://<BACKEND_HOST>/ (example: http://localhost:8000/)

Authentication: None implemented by default (open public endpoints). If you add auth later, update the frontend accordingly.

Notes about translations:
- Several models use django-parler translations. For those endpoints the serializer returns a `translations` object containing the translated fields per language.
- Many endpoints accept a `lang` query parameter (used in some views). If not provided, a default is used (often `uz` or `en` depending on view).

Endpoints
---------
1) GET /banner/?lang=<lang>
- Purpose: Return banners in a requested language.
- Query params: `lang` (optional; default `'en'` in code)
- Response: JSON array of objects: `{ name, image, alt }`.
  - `image` is an absolute URL if an image exists, otherwise `null`.
- Example request:
  - GET /banner/?lang=en
- Example response:
  [
    {
      "name": "Summer Sale",
      "image": "http://localhost:8000/media/banners/xxx.jpg",
      "alt": "Sale banner"
    }
  ]

2) GET /partners/
- Purpose: Return list of partners
- Response: array of partner objects serialized with `id`, `name`, `image` (URL path produced by DRF ImageField serializer; depending on serializer context you may receive relative path — views mostly pass serializer without `request` for Partners so image may be a relative path).

3) GET /products/
- Purpose: List products (optionally filtered by category)
- Query params:
  - `category_slug` (optional, category translated slug) — preferred for language-aware filtering
  - `category` (optional, numeric category id) — still supported as a fallback
- Response: [{ id, translations, sku, price, category }, ...]
  - `translations` is an object with language keys containing translated fields (name, description, slug).
  - `category` is the category id (foreign key).
- Examples:
  - GET /products/?category_slug=electronics&lang=en
  - GET /products/?category=2

4) GET /products/<slug:slug>/?lang=<lang>
- Purpose: Retrieve a single product by its translated slug.
- Notes: The backend expects the slug in the URL (`products/<slug>/`) and uses `lang` query param to select translation.
- Response: `{ id, translations, sku, price, category }` (same shape as list item)
- Example: GET /products/some-product-slug/?lang=uz

5) GET /product-images/?product=<product_id>
- Purpose: List images for a product
- Query params: `product` (product id)
- Response: [{ id, product, image, alt, ordering }, ...]
- Note: Views include `request` in serializer context in some places; images may be absolute URLs when `request` is passed.

6) GET /certificates/
- Purpose: Returns certificates (images)
- Response: [{ id, image, ordering }, ...]

7) GET /categories/
- Purpose: List all categories
- Response: [{ id, translations, image }, ...]
  - `translations` holds name, slug per language.

8) GET /categories/<slug:slug>/
- Purpose: Category detail by translated slug (use `?lang=` to select language when needed)
- Response: `{ id, translations, image }`

9) GET /companies/
- Purpose: Return company records (usually a single item)
- Response: [{ id, translations, phone, email, website }, ...]

10) GET /service/ (or /service-locations/ depending on router)
- Purpose: Return service center locations
- Response: [{ id, city, address, phone, email, map_url, description }, ...]
  - `city` is the `City` id.
  - `description` is an id referencing `ServiceCenterDescription`.

11) GET /service-center-descriptions/?lang=<lang>
- Purpose: Return descriptions translated per language
- Response: [{ id, title, description }, ...]

12) GET /cities/
- Purpose: List cities
- Response: [{ id, name }, ...]

Other notes
-----------
- Image fields: When the serializer is passed the `request` in the context, DRF's ImageField will typically output absolute URLs. Some views pass `context={'request': request}` and some don't — expect a mix of absolute URLs and relative paths. If you need absolute URLs consistently, either update the backend to always pass `request` into the serializer context, or construct image URLs in the frontend from `MEDIA_URL`.
- Translations shape: `translations` is returned by `parler_rest.serializers.TranslatedFieldsField`. It usually looks like:
  {
    "uz": { "name": "...", "slug": "...", ... },
    "en": { "name": "...", "slug": "...", ... },
    "ru": { ... }
  }

Errors and status codes
-----------------------
- Successful GETs: 200
- Not found: 404 (when retrieving a single object by slug/PK)
- The project currently doesn't implement authentication or 4xx/5xx error formats explicitly; expect default DRF responses.

API Contract (short)
- Inputs: HTTP GET with optional query params (lang, product, category, etc.)
- Outputs: JSON objects/arrays described above
- Errors: Standard DRF/Django errors (404 for missing resources)

AI prompt for frontend developer
--------------------------------
Use the following prompt to provide to an AI or a frontend engineer to build the UI/consumer for these endpoints. Save this prompt file into the repo as-is and feed it to your frontend AI agent.

---

You are building a frontend (React/Vue/Svelte — choose a modern SPA) that will consume a Django REST API. The backend base URL is: `http://localhost:8000/`.

Requirements:
1. Implement the following pages/components:
   - Homepage with banner carousel (GET /banner/?lang=en)
  - Products listing page with optional filtering by category (GET /products/?category_slug=<slug>)
   - Product detail page, loaded by slug (GET /products/<slug>/?lang=<lang>)
  - Category listing and category detail page (GET /categories/ and GET /categories/<slug>/)
   - Partners and certificates sections (GET /partners/, GET /certificates/)
   - Company info page (GET /companies/)
   - Service centers map/list (GET /service/ and GET /service-center-descriptions/?lang=<lang>)
   - Cities listing for a city selector (GET /cities/)

2. Networking guide for the frontend (how to call APIs and what to expect):
   - Use fetch() or axios. Example using fetch:

  ```js
  // Prefer slug-based category filtering for translated slugs
  const res = await fetch('http://localhost:8000/products/?category_slug=electronics&lang=en');
  if (!res.ok) throw new Error('Network error');
  const products = await res.json();
  // products: [{ id, translations, sku, price, category }, ...]
  ```

   - For product detail by slug:

     ```js
     const res = await fetch(`http://localhost:8000/products/${encodeURIComponent(slug)}/?lang=uz`);
     const product = await res.json();
     ```

   - For images: inspect the field returned by the endpoint. If image values are relative paths, prepend the backend host + MEDIA_URL (e.g. `http://localhost:8000/media/`). If values are absolute, use them directly.

3. Expected JSON shapes and how to map to UI components:
   - Banner: `{ name, image, alt }` → carousel slides
   - Product list item: `translations` → use `translations[chosenLang].name` or fallback; `price` → show price; `sku` → optional
   - Product detail: `translations[lang].description` → product description
   - Category: `translations[lang].name` and `image`

4. Localization:
   - Provide a language selector; for each fetch include `?lang=<code>` when the endpoint supports `lang`.
   - For endpoints that return translations arrays (object keyed by language), prefer using the returned translations in the response rather than requesting a different `lang` param; both approaches are used in the backend.

5. Error handling:
   - Display friendly messages for 404s (product not found) and network errors.

6. CORS:
   - Backend sets CORS to allow all origins in settings (CORS_ALLOW_ALL_ORIGINS = True), so frontend can call directly.

7. Deliverables from frontend AI:
   - Minimal SPA with routes/pages listed above
   - Components: BannerCarousel, ProductList, ProductCard, ProductDetail, CategoryList, PartnerGrid, CertificatesGallery, CompanyInfo, ServiceCenters
   - Use environment variable for API_BASE_URL (default http://localhost:8000)
   - Provide instructions to run the frontend locally (install, dev, build)

Optional notes for implementer (backend hints):
- If you need consistent absolute image URLs, ask the backend author to always pass `request` into serializer context.
- Product slug lookup uses translated slugs; the frontend must request the same language the slug was created for or use the translated slug from `/products/` response.

---

If you want, I can generate a sample React app skeleton that implements these endpoints and components, or a Postman/Insomnia collection of these endpoints for quick frontend testing.

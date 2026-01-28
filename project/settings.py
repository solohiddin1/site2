import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django_extensions',
    'parler',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_yasg',
    'drf_spectacular',
    # New modular apps
    'apps.categories',
    'apps.products',
    'apps.company',
    'apps.services',
    # 'app',
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'django_json_widget',
]

PARLER_LANGUAGES = {
    None: (
        {'code': 'uz', 'name': 'Uzbek'},
        {'code': 'en', 'name': 'English'},
        {'code': 'ru', 'name': 'Russian'},
    ),
    'default': {
        'fallbacks': ['uz'],  # default language if translation missing
        'hide_untranslated': False,
    }
}

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Custom middleware
    'apps.company.middleware.ExceptionMiddleware',
    'apps.company.middleware.RequestResponseLoggingMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'uz'  # Default language

# Available languages for Django (matches Parler languages)
LANGUAGES = [
    ('uz', 'Uzbek'),
    ('en', 'English'),
    ('ru', 'Russian'),
]

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CKEDITOR_UPLOAD_PATH = "uploads/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'
STATICFILES_DIRS = [
    BASE_DIR / 'site2/static'
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:8080',
    'https://7f0a7e0d2031.ngrok-free.app',
    'http://209.38.235.118',
    'https://209.38.235.118',
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:8080',
]

BACKEND_URL = 'http://localhost:8001'
CORS_ALLOW_CREDENTIALS = True

# If you want to allow all headers, use the following:
CORS_ALLOW_ALL_HEADERS = True
# Or keep the explicit list:
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024


JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "Gidrox Admin",

    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "Gidrox Admin",

    # Title on the brand (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_brand": "Gidrox ",
    # "site_logo": "jazzmin/img/nonborlogo.png",
    "order_with_respect_to": ["products", "company", "categories", "services", "users"],
    # "site_logo": "img/admin_logo.png",        # path to logo in STATIC
    # "login_logo": "img/admin_logo_large.png", # optional large logo on login page
    "user_avatar": "image",

    "language_chooser": True,
    "show_ui_builder": True,

    "custom_links": {
        "products.Product": [
            {
                "name": "Checking Products",
                "url": "admin:products_product_changelist",
                "icon": "fas fa-box",
                "permissions": ["products.view_product"],
            }
        ],
    }
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')



REDIS_URL = "redis://localhost:6379/7"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'KEY_PREFIX': 'nonbor',
        'TIMEOUT': 300,
    }
}

# Session'ni database'da saqlash (Redis memory leak oldini olish)
# Redis session cache vaqt o'tishi bilan memory to'ldiradi
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600  # 2 hafta
SESSION_SAVE_EVERY_REQUEST = False  # Har request'da save qilmaslik (performance)
SESSION_COOKIE_SECURE = not DEBUG  # Production'da HTTPS orqali
SESSION_COOKIE_HTTPONLY = True  # XSS himoyasi

BASE_URL = os.getenv('BASE_URL', 'http://localhost:8080')

# Django settings for videochat project.

import os
from pathlib import Path
import socket # Keep for get_local_ip if you still want to use it for debugging/reference

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CORE SETTINGS ---
# SECURITY WARNING: keep the secret key used in production secret!
# Use environment variable for production, fallback to a development key locally.
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-4ee@u+h--6(1cxaush=7d)v1hshyq&oby@s__5uw^_5mjz7^(6" # This is your dev key
)

# SECURITY WARNING: don't run with debug turned on in production!
# Use environment variable for production, default to True for local development.
DEBUG = bool(os.environ.get("DEBUG", default=1)) # default=1 makes DEBUG True for local

# ALLOWED_HOSTS configuration
# For development within Docker, '*' is often simplest, but be cautious in production.
# The custom get_local_ip() and specific IP ranges are largely redundant if '*' is used
# or if hosts are properly managed via environment variables/ngrok.
if DEBUG:
    ALLOWED_HOSTS = ['*'] # Allows all hosts when DEBUG is True, useful for Docker/ngrok
else:
    # In production, get hosts from environment variable and make it specific
    ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1").split(",")

# Optional: You can keep this function if you specifically need the host's local IP for other purposes,
# but it's generally not directly used by ALLOWED_HOSTS in a Docker setup with '*' or ngrok.
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return '127.0.0.1'

# LOCAL_IP = get_local_ip() # Uncomment if you still want to log or use this IP elsewhere

# Application definition
INSTALLED_APPS = [
    "daphne",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'video', # Your custom app
    'channels',
    'corsheaders',
    'rest_framework', # If you are using Django Rest Framework
]

MIDDLEWARE = [
    # CORS middleware should be very high, preferably right after SecurityMiddleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'videochat.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Use Pathlib for DIRS
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

WSGI_APPLICATION = 'videochat.wsgi.application'
ASGI_APPLICATION = 'videochat.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],  # Use Redis service name from Docker Compose
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',  # Use Redis service name from Docker Compose
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

REDIS_HOST = os.environ

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'


CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True # Important if you're sending cookies/auth headers


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
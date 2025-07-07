"""
Django settings for evento_qr project - Docker version.
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!!cc&lrmf-k)4$)#+7k(00osv62%(($$77wsr5@_vd(lf&)z7='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    '127.0.0.1', 
    'localhost',
    '0.0.0.0',
    '*',  # Para desarrollo
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders', 
    'invitados',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para servir archivos estáticos
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuración CORS - ACTUALIZADO CON PUERTO 3012
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3012",      # ← NUEVO: Puerto 3012
    "http://127.0.0.1:3012",      # ← NUEVO: Puerto 3012
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
]
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'evento_qr.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'evento_qr.wsgi.application'

# Database configuration for Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'evento_qr_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'Saladin0'),
        'HOST': os.getenv('DB_HOST', 'db'),  # 'db' es el nombre del servicio en docker-compose
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Password validation
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
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuración de WhiteNoise para servir archivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URLs de autenticación
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Configuración CSRF para Docker - ACTUALIZADO CON PUERTO 3012
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:3012',      # ← NUEVO: Puerto 3012
    'http://localhost:3012',      # ← NUEVO: Puerto 3012
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://0.0.0.0:8000',
    'https://*.ngrok-free.app',   # Para ngrok si lo usas
    'https://*.ngrok.io',
    'https://*.ngrok.app',
    'http://*.ngrok-free.app',
]

# Configuración adicional para contenedores
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# Configuración adicional para PWA (del settings original)
# Si necesitas configuraciones específicas de tu proyecto, agrégalas aquí

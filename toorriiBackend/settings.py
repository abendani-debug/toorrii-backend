from pathlib import Path
import os
from decouple import config
from datetime import timedelta

# =======================
# BASE DIR
# =======================
BASE_DIR = Path(__file__).resolve().parent.parent

# =======================
# SECRET KEY / DEBUG / HOSTS
# =======================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config("DEBUG", cast=bool, default=True)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1",
    cast=lambda v: [h.strip() for h in v.split(",") if h]
)

# =======================
# APPLICATIONS
# =======================
INSTALLED_APPS = [
    "corsheaders",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps personnalisées
    'adminToorrii',
    'authentication',
    'professionnel',
    'client',
    'home',

    # REST / JWT / Auth
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'rest_framework.authtoken',
    "dj_rest_auth.registration",

    # Documentation
    'drf_spectacular',
]

SITE_ID = 1

# =======================
# AUTHENTICATION
# =======================
AUTH_USER_MODEL = "adminToorrii.Utilisateur"  # Modèle utilisateur principal

# Allauth / signup / login fields
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_LOGIN_FIELDS = ["email"]
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"

REST_USE_USERNAME = False
REST_USE_JWT = True

# =======================
# REST FRAMEWORK
# =======================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# =======================
# SIMPLE JWT
# =======================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=20),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "USER_ID_FIELD": "utilisateur_id",
    "USER_ID_CLAIM": "user_id",  # claim personnalisé pour JWT
}

# =======================
# SOCIAL ACCOUNT / GOOGLE
# =======================
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

#google Oauth config
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET=config('GOOGLE_CLIENT_SECRET')

#Facebook Oauth config
FACEBOOK_APP_ID = config('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = config('FACEBOOK_APP_SECRET')

# =======================
# CSRF
# =======================
CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_HTTPONLY = False      # accessible par JS
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", cast=bool, default=True)
# Frontend (Vercel) et backend (Render) sont sur des domaines différents :
# le cookie doit pouvoir être renvoyé sur une requête cross-site.
CSRF_COOKIE_SAMESITE = "None" if not DEBUG else "Lax"
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost:5173,http://127.0.0.1:5173",
    cast=lambda v: [h.strip() for h in v.split(",") if h]
)

# =======================
# CORS
# =======================
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", cast=bool, default=False)
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5173,http://127.0.0.1:5173",
    cast=lambda v: [h.strip() for h in v.split(",") if h]
)
CORS_ALLOW_HEADERS = [
    "authorization",
    "content-type",
    "x-csrftoken",
    "accept",
    "origin",
]

# =======================
# MIDDLEWARE
# =======================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# =======================
# URLS / TEMPLATES / WSGI
# =======================
ROOT_URLCONF = 'toorriiBackend.urls'
WSGI_APPLICATION = 'toorriiBackend.wsgi.application'

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

# =======================
# DATABASE
# =======================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# =======================
# MEDIA / STATIC
# =======================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =======================
# PASSWORD VALIDATORS
# =======================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# =======================
# INTERNATIONALIZATION
# =======================
LANGUAGE_CODE = 'fr'
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# =======================
# DJ REST AUTH REDIRECT
# =======================
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# =======================
# DRF SPECTACULAR
# =======================
SPECTACULAR_SETTINGS = {
    'TITLE': 'Mon API Toorrii',
    'DESCRIPTION': 'Description des API pour Toorrii',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}


# BREVO conf

BREVO_API_KEY = config('BREVO_API_KEY') 
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL') 
DEFAULT_FROM_NAME = config('DEFAULT_FROM_NAME') 


SECURE_CROSS_ORIGIN_OPENER_POLICY = None


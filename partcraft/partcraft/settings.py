"""
Django settings for partcraft project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os.path
from pathlib import Path
from datetime import timedelta

from django.conf import settings
import os
import dj_database_url


# from dotenv import load_dotenv
# load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-tnrr@^xourvp5u!tz$m__d-3nk6mp#1*ux)_27e251v)im5u$r'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'parts',
    'account',
    'rest_framework',
    'django_filters',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'django_elasticsearch_dsl',
    'django_elasticsearch_dsl_drf',
    'part_admin',
    'part_search',
    'corsheaders',
]

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
}

ELASTICSEARCH_DSL = {
    'default' : {
        "hosts" : "https://site:bcc6798cdf8064c30f8f94c0a74c66e6@oin-us-east-1.searchly.com",
        # "hosts":"localhost:9200",
    }
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'partcraft.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'partcraft.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'postgres',
#         'USER': 'postgres',
#         'PASSWORD': 'ad3infotech',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "rediss://red-crfd0cij1k6c73dkkvag:mJY0M3bkRjABZFEFvW9ymYKVvhdWPWrO@oregon-redis.render.com:6379/1",  # Use the appropriate REDIS_HOST, REDIS_PORT, and REDIS_PASSWORD
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "mJY0M3bkRjABZFEFvW9ymYKVvhdWPWrO"  # Add password if Redis is password protected
        }
    }
}

# Optional: Session storage with Redis
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.bjtqyojwojqfmxrxcqcv',
        'PASSWORD': 'gmJqKZh3XxcW8KCF',
        'HOST': 'aws-0-ap-southeast-1.pooler.supabase.com',
        'PORT': '6543',
    },
    'nonrel': {
        'ENGINE': 'djongo',
        'NAME': 'partscraft',
        'ENFORCE_SCHEMA': False,
        'CLIENT': {
            'host': 'mongodb+srv://admin:kWwviQLhdkbL5MQE@admindash.zvg2l7k.mongodb.net/?retryWrites=true&w=majority',
        },
    }
}

# DATABASE_ROUTERS = ['parts.utils.db_routers.NonRelRouter']
MONGOENGINE = {
    'db': 'partscraft',
    'host': 'mongodb+srv://admin:kWwviQLhdkbL5MQE@admindash.zvg2l7k.mongodb.net/?retryWrites=true&w=majority',
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': os.environ.get("DB_NAME"),
#         'USER': os.environ.get("DB_USER"),
#         'PASSWORD': os.environ.get("DB_PASSWORD"),
#         'HOST': os.environ.get("DB_HOST"),
#         'PORT': os.environ.get("DB_PORT"),
#     }
# }
# DATABASES["default"] = dj_database_url.parse("postgresql://postgres.bjtqyojwojqfmxrxcqcv:gmJqKZh3XxcW8KCF@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres")

# DATABASES["default"]=dj_database_url.parse("postgres://partcraft_render_l8s8_user:RcJrxzEJMoDmraOc0jJcJRXLmGKoaA5n@dpg-cppu4ddds78s73ees2q0-a.oregon-postgres.render.com/partcraft_render_l8s8")

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = os.path.join(BASE_DIR, 'static'),
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')



MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'account.User'

#simple jwt setting
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=10),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": settings.SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}

PASSWORD_RESET_TIMEOUT = 1800

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'dhanushpathiprakash@ad3infotech.com'
EMAIL_HOST_PASSWORD = 'Sixty^(69'

import mongoengine

mongoengine.connect(
    db=MONGOENGINE['db'],
    host=MONGOENGINE['host'],
    alias='nonrel',
)

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

CORS_ALLOW_CREDENTIALS = True


CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://partcraft-a2ti.onrender.com',
]


CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

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

SESSION_COOKIE_SAMESITE ='None'
SESSION_COOKIE_SECURE = True
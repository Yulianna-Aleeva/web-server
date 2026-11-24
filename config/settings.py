import os
from dotenv import load_dotenv
from pathlib import Path

# Загружаем переменные из .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-6sgov=^ght(oe_redn2mmabas)3=!@(%n&no80(43^6zryw+%l'

DEBUG = True

ALLOWED_HOSTS = []

GIGACHAT_CREDENTIALS = os.getenv('GIGACHAT_CREDENTIALS')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'catalog',
    'blogs',
    # === ОБЛАЧНОЕ ХРАНИЛИЩЕ SUPABASE STORAGE ===
    # 'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT', default='5432'),
        'CONN_MAX_AGE': 0,
        'CONN_HEALTH_CHECKS': True,
        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}

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

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Asia/Yekaterinburg'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === ЛОКАЛЬНОЕ ХРАНИЛИЩЕ МЕДИАФАЙЛОВ (активно сейчас) ===
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# === ОБЛАЧНОЕ ХРАНИЛИЩЕ SUPABASE STORAGE ===
# USE_CLOUD_STORAGE = os.getenv('USE_CLOUD_STORAGE', 'True') == 'True'
#
# if USE_CLOUD_STORAGE:
#     STORAGES = {
#         "default": {
#             "BACKEND": "storages.backends.s3.S3Storage",
#             "OPTIONS": {
#                 "access_key": os.getenv("SUPABASE_S3_ACCESS_KEY_ID"),
#                 "secret_key": os.getenv("SUPABASE_S3_SECRET_ACCESS_KEY"),
#                 "bucket_name": os.getenv("SUPABASE_BUCKET_NAME"),
#                 "endpoint_url": os.getenv("SUPABASE_S3_ENDPOINT_URL"),
#                 "region_name": "eu-west-1",
#                 "querystring_auth": False,
#                 "addressing_style": "path",
#                 "custom_domain": "qdwbkbukaxfgboniokmo.supabase.co/storage/v1/object/public/products",
#             },
#         },
#         "staticfiles": {
#             "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
#         },
#     }


# === НАСТРОЙКИ ОТПРАВКИ ПОЧТЫ (вывод писем в консоль - АКТИВНО) ===
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@my-relax.ru'

# === РЕАЛЬНАЯ ПОЧТА ===
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.yandex.ru')
# EMAIL_PORT = int(os.getenv('EMAIL_PORT', 465))
# EMAIL_USE_SSL = True
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

"""
Django settings for ims project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os
import django_heroku
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-bjybtte)y^lc!lu2ndz3s21@r_y5syjo3#u$pq=_-w!-081q0e'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# ALLOWED_HOSTS = ['invenotry-ms.herokuapp.com', '127.0.0.1']
ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'www.apps.WwwConfig',
    'rest_framework',
    'djoser',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_extensions'

]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

DJOSER = {
    'LOGIN_FIELD': 'email',
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',

]


CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:19000', # Replace with the origin you want to allow
    'http://192.168.1.184:19000', # Replace with the origin you want to allow
    'exp://192.168.1.184', # Replace with the origin you want to allow
]

ROOT_URLCONF = 'ims.urls'

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

WSGI_APPLICATION = 'ims.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# connecting to posgresql
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': 'mydatabase',
#     }
# }


DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': 'd57l14eo4kj584',
       'USER': 'epfamqixllpddb',
       'PASSWORD': '294cbdd21b8e10ce7f39599abeb2860e93a73330dc52d63eed3d046d799ea1bc',
       'HOST': 'ec2-52-30-67-143.eu-west-1.compute.amazonaws.com',
       'PORT': '5432',
   }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_FROM = 'bokiev.khushnud@gmail.com'
EMAIL_HOST_USER = 'bokiev.khushnud@gmail.com'
EMAIL_HOST_PASSWORD = 'jqebbjihabmhduhc'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
PASSWORD_RESET_TIMEOUT = 14400


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('ru', 'Russian'),
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]


# Static files (CSS, JavaScripMEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'

# Static
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
django_heroku.settings(locals())
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
X_FRAME_OPTIONS = "SAMEORIGIN"


# Celery settings

# CELERY_BROKER_URL = 'redis://localhost:6379/0'  # replace with your broker URL
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'  # replace with your backend URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# redis for heroku
CELERY_BROKER_URL = os.environ.get('REDISCLOUD_URL', 'redis://default:EtlstfCjAPW0mQ9tnUnP45bCXuVgNtDh@redis-15008.c3.eu-west-1-2.ec2.cloud.redislabs.com:15008')
CELERY_RESULT_BACKEND = os.environ.get('REDISCLOUD_URL', 'redis://default:EtlstfCjAPW0mQ9tnUnP45bCXuVgNtDh@redis-15008.c3.eu-west-1-2.ec2.cloud.redislabs.com:15008')
# ...


CELERY_BEAT_SCHEDULE = {
    'send_due_date_notification': {
        'task': 'www.tasks.send_due_date_notification',
        'schedule': timedelta(days=1),
    },
    'send_expiry_notification': {
        'task': 'www.tasks.send_expiry_notification',
        'schedule': timedelta(days=1),
    },
}

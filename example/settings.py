"""
Django settings for bcpp_interview project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from unipath import Path
from django.utils import timezone

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(os.path.dirname(os.path.realpath(__file__)))
APP_LABEL = 'example'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4w#xs+=lrx4$mmqv+vzy^9i!(sni2eh=q_-9(#w4r20sv($2af'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TASTYPIE_FULL_DEBUG = True
ALLOWED_HOSTS = ['localhost']


# Application definition

DEPENDENCY_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'django_revision',
    'tastypie',
    'crispy_forms',
    'simple_history',
    'edc_base',
]

EXAMPLE_APPS = [
    'example.apps.SyncAppConfig',
    'example.apps.DjangoCryptoFieldsApp',
    'example.apps.ExampleAppConfig',
]

INSTALLED_APPS = DEPENDENCY_APPS + EXAMPLE_APPS

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'example.urls'

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
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'example.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
SQLITE3_DBNAME = 'db.sqlite3'
DATABASES = {
    # required for tests when acting as a server that deserializes
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, SQLITE3_DBNAME),
    },
    # required for tests when acting as a server but not attempting to deserialize
    'server': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, SQLITE3_DBNAME),
    },
    # required for tests when acting as a client
    'client': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, SQLITE3_DBNAME),
    },
    'test_server': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, SQLITE3_DBNAME),
    },
}

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Gaborone'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR.child('static')
MEDIA_ROOT = BASE_DIR.child('media')
MEDIA_URL = '/media/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


GIT_DIR = BASE_DIR.ancestor(1)
KEY_PATH = os.path.join(BASE_DIR.ancestor(1), 'crypto_fields')
SHOW_CRYPTO_FORM_DATA = True
STUDY_OPEN_DATETIME = timezone.datetime(2016, 1, 18)
LANGUAGES = (
    ('tn', 'Setswana'),
    ('en', 'English'),
)
DEVICE_ID = '15'
SERVER_DEVICE_ID_LIST = ['99']
# MIDDLEMAN_DEVICE_ID_LIST = []
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# django-cors-headers
# CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    'localhost:8000',
    'localhost:8001',
)

"""
Django settings for dit_helpdesk project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from os.path import join as join_path

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.environ.get(
    'DJANGO_BASE_DIR',
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'a-secret-key')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'psqlextra',
    'core',
    'commodities',
    'cookies',
    'countries',
    'feedback',
    'hierarchy',
    'index',
    'rules_of_origin',
    'search',
    'privacy_terms_and_conditions',
    'trade_tariff_service',
    'django_extensions',
    'authbroker_client',
    'user',
    'regulations'
]


MIDDLEWARE = [
    # 'django.middleware.cache.UpdateCacheMiddleware',
    # 'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.AdminIpRestrictionMiddleware',
    #'requirements_documents.middleware.RedirectExceptionMiddleware',
    #'django.middleware.cache.FetchFromCacheMiddleware',
]

ROOT_URLCONF = 'dit_helpdesk.urls'

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

WSGI_APPLICATION = 'dit_helpdesk.wsgi.application'

DATABASES = {
   'default': dj_database_url.config()
}

HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10


DATA_UPLOAD_MAX_NUMBER_FIELDS = 85000  # default is 1000

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        #'LOCATION': '/var/run/redis/redis.sock',
        'LOCATION': 'localhost:6379',
    },
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch5_backend.Elasticsearch5SearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'authbroker_client.backends.AuthbrokerBackend',
]


FIXTURE_DIRS = (
    'countries/fixtures/',
)

# SESSION_EXPIRE_AT_BROWSER_CLOSE = False
# SESSION_COOKIE_AGE = 5 * 60


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/


STATIC_URL = '/assets/'
STATICFILES_DIRS = [
    join_path(BASE_DIR, 'static_collected'),
]

STATIC_ROOT = join_path(BASE_DIR, 'static')  # manage.py collectstatic will copy static files here

MEDIA_ROOT = join_path(BASE_DIR, 'media')
MEDIA_URL = '/files/'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    #'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'sass_processor.finders.CssFinder',
]

#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # compression and cachine
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'  # compression without caching

# The correct index of the client IP in the X-Forwarded-For header.  It should be set to
# -2 if accessing the private domain and -3 if accessing the site via the public URL.
IP_SAFELIST_XFF_INDEX = int(os.environ.get('IP_SAFELIST_XFF_INDEX', '-2'))

RESTRICT_ADMIN = os.environ.get('RESTRICT_ADMIN', 'True') == 'True'
ALLOWED_ADMIN_IPS = os.environ.get('ALLOWED_ADMIN_IPS', '127.0.0.1').split(',')
ALLOWED_ADMIN_IP_RANGES = os.environ.get('ALLOWED_ADMIN_IP_RANGES', '127.0.0.1/32').split(',')

# authbroker config
AUTHBROKER_URL = os.environ.get('AUTHBROKER_URL', '')
AUTHBROKER_CLIENT_ID = os.environ.get('AUTHBROKER_CLIENT_ID', '')
AUTHBROKER_CLIENT_SECRET = os.environ.get('AUTHBROKER_CLIENT_SECRET', '')

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/admin/login/'

AUTH_USER_MODEL = 'user.User'

FEEDBACK_MAX_LENGTH = 1000

# trade tariff service arguments
IMPORT_DATA_PATH = BASE_DIR+"/trade_tariff_service/import_data/{0}"
TRADE_TARIFF_SERVICE_BASE_URL = "https://www.trade-tariff.service.gov.uk/trade-tariff/"
TRADE_TARIFF_SERVICE_COMMODITIES_JSON_PATH = "commodities/{0}.json?currency=EUR&day=1&month=1&year=2019"
TRADE_TARIFF_SERVICE_SECTION_URL = "https://www.trade-tariff.service.gov.uk/trade-tariff/sections/{0}.json"
TRADE_TARIFF_SERVICE_MODEL_ARGS=["Section", "Chapter", "Heading", "SubHeading", "Commodity"]

# regulation import arguments
REGULATIONS_MODEL_ARG=["Regulation"]
REGULATIONS_DATA_PATH=BASE_DIR+"/regulations/data/{0}"
RULES_OF_ORIGIN_DATA_PATH=BASE_DIR+"/rules_of_origin/data/{0}"

# Secure cookie settings.
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True




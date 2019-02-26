"""
Django settings for dit_helpdesk project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import environ

root = environ.Path(__file__) - 4
env = environ.Env(
    DEBUG=(bool, False),
    BASICAUTH_DISABLE=(bool, False),
)

DEBUG=env('DEBUG')
BASICAUTH_DISABLE=env('BASICAUTH_DISABLE')
BASICAUTH_USERS=env.json('BASICAUTH_USERS')


#environ.Env.read_env(f'{root}/local.env')

SITE_ROOT = root()

from os.path import join as join_path

# import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'psqlextra',
    'haystack',
    'haystackbrowser',

    'core',
    'commodities',
    'countries',
    'hierarchy',
    'rules_of_origin',
    'search',
    'trade_tariff_service',
]

# Temporary BasicAuth - NB setting BASICAUTH_DISABLE=1 environment var dynamically disables
MIDDLEWARE = [
    'basicauth.middleware.BasicAuthMiddleware',  # Temporary
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

# Remove after v4
#WSGI_APPLICATION = 'dit_helpdesk.wsgi.application'


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

FIXTURE_DIRS = (
   'countries/fixtures/',
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 15 * 60


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
    join_path(BASE_DIR, 'static'),
    join_path(BASE_DIR, 'govuk_template_assets'),
    # os.path.join(BASE_DIR, 'node_modules'),
]

STATIC_ROOT = join_path(BASE_DIR, 'static_collected')  # manage.py collectstatic will copy static files here

MEDIA_ROOT = join_path(BASE_DIR, 'media')
MEDIA_URL = '/files/'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    #'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'sass_processor.finders.CssFinder',
]

#STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # compression and cachine
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'  # compression without caching

# a list of (measure_type_id, measure_type_series_id) values that are relevant
# we will ignore measures that are not in this list.
TTS_MEASURE_TYPES = [
    ('103', 'C'), ('105', 'C'), ('106', 'C'), ('112', 'C'), ('115', 'C'),
    ('117', 'C'), ('119', 'C'), ('122', 'C'), ('123', 'C'), ('140', 'C'),
    ('141', 'C'), ('142', 'C'), ('143', 'C'), ('144', 'C'), ('145', 'C'),
    ('146', 'C'), ('147', 'C'), ('901', 'C'), ('902', 'C'), ('903', 'C'),
    ('906', 'C'), ('907', 'C'), ('919', 'C'), ('305', 'P'), ('VTA', 'P'),
    ('VTE', 'P'), ('VTS', 'P'), ('VTZ', 'P'), ('306', 'Q'), ('DAA', 'Q'),
    ('DAB', 'Q'), ('DAC', 'Q'), ('DAE', 'Q'), ('DAI', 'Q'), ('DBA', 'Q'),
    ('DBB', 'Q'), ('DBC', 'Q'), ('DBE', 'Q'), ('DBI', 'Q'), ('DCA', 'Q'),
    ('DCC', 'Q'), ('DCE', 'Q'), ('DCH', 'Q'), ('DDA', 'Q'), ('DDB', 'Q'),
    ('DDC', 'Q'), ('DDD', 'Q'), ('DDE', 'Q'), ('DDF', 'Q'), ('DDG', 'Q'),
    ('DDJ', 'Q'), ('DEA', 'Q'), ('DFA', 'Q'), ('DFB', 'Q'), ('DFC', 'Q'),
    ('DGC', 'Q'), ('DHA', 'Q'), ('DHC', 'Q'), ('DHE', 'Q'), ('EAA', 'Q'),
    ('EAE', 'Q'), ('EBA', 'Q'), ('EBB', 'Q'), ('EBE', 'Q'), ('EBJ', 'Q'),
    ('EDA', 'Q'), ('EDB', 'Q'), ('EDE', 'Q'), ('EDJ', 'Q'), ('EEA', 'Q'),
    ('EEF', 'Q'), ('EFA', 'Q'), ('EFJ', 'Q'), ('EGA', 'Q'), ('EGB', 'Q'),
    ('EGJ', 'Q'), ('EHI', 'Q'), ('EIA', 'Q'), ('EIB', 'Q'), ('EIC', 'Q'),
    ('EID', 'Q'), ('EIE', 'Q'), ('EIJ', 'Q'), ('EXA', 'Q'), ('EXB', 'Q'),
    ('EXC', 'Q'), ('EXD', 'Q'), ('FAA', 'Q'), ('FAE', 'Q'), ('FAI', 'Q'),
    ('FBC', 'Q'), ('FBG', 'Q'), ('LAA', 'Q'), ('LAE', 'Q'), ('LBA', 'Q'),
    ('LBB', 'Q'), ('LBE', 'Q'), ('LBJ', 'Q'), ('LDA', 'Q'), ('LEA', 'Q'),
    ('LEF', 'Q'), ('LFA', 'Q'), ('LGJ', 'Q'),

    # seems to also be necessary for commodity: 0202309075
    ('710', 'UNKNOWN'),
]

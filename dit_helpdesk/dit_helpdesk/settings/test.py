"""
With these settings, tests run faster.
"""
import logging.config
import os
import re

DEBUG = True
from django.utils.log import DEFAULT_LOGGING

from .base import *

ADMIN_ENABLED = True

if ADMIN_ENABLED is True:
    INSTALLED_APPS.append('django.contrib.admin',)

if ADMIN_ENABLED is True:
    RESTRICT_ADMIN = os.environ.get('RESTRICT_ADMIN', 'True') == 'True'
    ALLOWED_ADMIN_IPS = os.environ.get('ALLOWED_ADMIN_IPS', '127.0.0.1').split(',')
    ALLOWED_ADMIN_IP_RANGES = os.environ.get('ALLOWED_ADMIN_IP_RANGES', '127.0.0.1/32').split(',')

if ADMIN_ENABLED is True:
    LOGIN_REDIRECT_URL = '/admin/login/'

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", default="0GU5hi1N7kOZ3jcKZbVrk1CXX9MAnLOiuDyEyqIvAej2Tj7KlrA3Ey7jGgeW3NVd")
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": ""
    }
}

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG  # noqa F405


DATABASES = {
    'default': {
        'ENGINE': 'psqlextra.backend',  # 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DJANGO_POSTGRES_DATABASE'),
        'USER': os.environ.get('DJANGO_POSTGRES_USER'),
        'PASSWORD': os.environ.get('DJANGO_POSTGRES_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

# Disable Django's logging setup
LOGGING_CONFIG = None

LOGLEVEL = os.environ.get('LOGLEVEL', 'info').upper()

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        # console logs to stderr
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        # Add Handler for Sentry for `warning` and above
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        # default for all undefined Python modules
        '': {
            'level': 'WARNING',
            'handlers': ['console', 'sentry'],
        },
        # Our application code
        'app': {
            'level': LOGLEVEL,
            'handlers': ['console', 'sentry'],
            # Avoid double logging because of root logger
            'propagate': False,
        },
        # Prevent noisy modules from logging to Sentry
        'noisy_module': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        # Default runserver request logging
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    },
})

# Test Data
TEST_COMMODITY_CODE = "0101210000"
TEST_COMMODITY_CODE_SPLIT = list(re.search('([0-9]{6})([0-9]{2})([0-9]{2})', TEST_COMMODITY_CODE).groups())
TEST_SUBHEADING_CODE = "0101210000"
TEST_HEADING_CODE = "0101000000"
TEST_CHAPTER_CODE = "0100000000"
TEST_SECTION_ID = "1"
TEST_COUNTRY_CODE = "AU"
TEST_COUNTRY_NAME = "Australia"
TEST_COMMODITY_DESCRIPTION = "Pure-bred breeding animals"
TEST_HEADING_DESCRIPTION = "Live horses, asses, mules and hinnies"
TEST_SUBHEADING_DESCRIPTION = "Horses"

COMMODITY_DATA = BASE_DIR + "/commodities/tests/commodity_{0}.json".format(TEST_COMMODITY_CODE)
COMMODITY_STRUCTURE = BASE_DIR + "/commodities/tests/structure_{0}.json".format(TEST_COMMODITY_CODE)
SUBHEADING_STRUCTURE = BASE_DIR + "/hierarchy/tests/subheading_{0}_structure.json".format(TEST_SUBHEADING_CODE)
HEADING_STRUCTURE = BASE_DIR + "/hierarchy/tests/heading_{0}_structure.json".format(TEST_HEADING_CODE)
CHAPTER_STRUCTURE = BASE_DIR + "/hierarchy/tests/chapter_{0}_structure.json".format(TEST_CHAPTER_CODE)
SECTION_STRUCTURE = BASE_DIR + "/hierarchy/tests/section_{}_structure.json".format(TEST_SECTION_ID)
COUNTRIES_DATA = BASE_DIR + "/countries/fixtures/countries_data.json"
SECTIONJSON_DATA = BASE_DIR + "/trade_tariff_Service/import_data/SectionJson.json"
CHAPTERJSON_DATA = BASE_DIR + "/trade_tariff_Service/import_data/ChapterJson.json"
HEADINGJSON_DATA = BASE_DIR + "/trade_tariff_Service/import_data/HeadingJson.json"
COMMODITYHEADINGJSON_DATA = BASE_DIR + "/trade_tariff_Service/import_data/CommodityHeadingJson.json"
IMPORTMEASUREJSON_DATA = BASE_DIR + "/trade_tariff_Service/import_data/ImportMeasureJson.json"

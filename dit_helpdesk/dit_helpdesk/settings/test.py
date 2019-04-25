"""
With these settings, tests run faster.
"""
import logging.config
import os

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
        'NAME': 'helpdesk2',
        'USER': 'ldluser',
        'PASSWORD': 'ldluser',
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
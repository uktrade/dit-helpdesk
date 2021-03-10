import os
import sys
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

import dj_database_url

from core.logging import UserLogFormatter

from .env import env

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APPS_DIR = os.path.join(BASE_DIR, "dit_helpdesk")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
IMPORTER_JOURNEY_HOST = env.str("IMPORTER_JOURNEY_HOST", '')

SECRET_KEY = env.str("DJANGO_SECRET_KEY")

ADMIN_ENABLED = env.bool("ADMIN_ENABLED")

READ_ONLY = True
CMS_ENABLED = False

# Feature flags
FLAGS = {
    "EU_FALLBACK": [],
}


# Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "elasticapm.contrib.django",
    "formtools",
    "flags",
    "core",
    "commodities",
    "cookies",
    "countries",
    "feedback",
    "contact",
    "iee_contact",
    "hierarchy",
    "index",
    "rules_of_origin",
    "search",
    "privacy_terms_and_conditions",
    "trade_tariff_service",
    "django_extensions",
    "authbroker_client",
    "user",
    "regulations",
    "healthcheck",
    "directory_forms_api_client",
    "rest_framework",
    "django_elasticsearch_dsl",
    "django_elasticsearch_dsl_drf",
    "accessibility",
    "reversion",
    "django_migration_linter",
    "polymorphic",
    "deferred_changes",
]

MIDDLEWARE = [
    "healthcheck.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "reversion.middleware.RevisionMiddleware",
    "core.middleware.AdminIpRestrictionMiddleware",
    "core.middleware.NoIndexMiddleware",
    "csp.middleware.CSPMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": False,
        "OPTIONS": {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.ga_gtm_processor",
                "core.context_processors.feature_flag_processor",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {"default": dj_database_url.config()}

DATA_UPLOAD_MAX_NUMBER_FIELDS = 85000  # default is 1000


# ELASTICSEARCH_DSL SETTINGS
# https://github.com/sabricot/django-elasticsearch-dsl
# https://django-elasticsearch-dsl-drf.readthedocs.io/en/latest/
# Name of the Elasticsearch index
ELASTICSEARCH_INDEX_NAMES = {
    "search.documents.section": "section",
    "search.documents.chapter": "chapter",
    "search.documents.heading": "heading",
    "search.documents.subheading": "subheading",
    "search.documents.commodity": "commodity",
}
ELASTICSEARCH_DSL_AUTO_REFRESH = False
ELASTICSEARCH_DSL_AUTOSYNC = False
# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "authbroker_client.backends.AuthbrokerBackend",
]

FIXTURE_DIRS = ("countries/fixtures/",)

# SESSION_EXPIRE_AT_BROWSER_CLOSE = False
# SESSION_COOKIE_AGE = 5 * 60


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "Europe/London"

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_THOUSAND_SEPARATOR = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/


STATIC_URL = "/assets/"
STATICFILES_DIRS = [os.path.join(APPS_DIR, "static_collected")]

STATIC_ROOT = os.path.join(
    APPS_DIR, "static"
)  # manage.py collectstatic will copy static files here

MEDIA_ROOT = os.path.join(APPS_DIR, "media")
MEDIA_URL = "/files/"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedStaticFilesStorage"
)  # compression without caching

# The correct index of the client IP in the X-Forwarded-For header.  It should be set to
# -2 if accessing the private domain and -3 if accessing the site via the public URL.
IP_SAFELIST_XFF_INDEX = env.int("IP_SAFELIST_XFF_INDEX")
RESTRICT_ADMIN = env.bool("RESTRICT_ADMIN")
ALLOWED_ADMIN_IPS = env.list("ALLOWED_ADMIN_IPS")
ALLOWED_ADMIN_IP_RANGES = env.list("ALLOWED_ADMIN_IP_RANGES")

# authbroker config
AUTHBROKER_URL = env.str("AUTHBROKER_URL")
AUTHBROKER_CLIENT_ID = env.str("AUTHBROKER_CLIENT_ID")
AUTHBROKER_CLIENT_SECRET = env.str("AUTHBROKER_CLIENT_SECRET")

LOGIN_URL = env.str("LOGIN_URL")

LOGIN_REDIRECT_URL = env.str("LOGIN_REDIRECT_URL")

AUTH_USER_MODEL = "user.User"

FEEDBACK_MAX_LENGTH = 1000
CONTACT_MAX_LENGTH = 1000

# Trade Tariff

# trade tariff service arguments
IMPORT_DATA_PATH = APPS_DIR + "/trade_tariff_service/import_data/{0}"


def get_trade_tariff_config():
    return {
        "UK": {
            "TREE": {
                "BASE_URL": "https://www.trade-tariff.service.gov.uk/api/v2/",
            },
            "JSON_OBJ": {
                "BASE_URL": "https://www.trade-tariff.service.gov.uk/api/v1/",
            },
        },
        "EU": {
            "TREE": {
                "BASE_URL": "https://www.trade-tariff.service.gov.uk/xi/api/v2/",
            },
            "JSON_OBJ": {
                "BASE_URL": "https://www.trade-tariff.service.gov.uk/xi/api/v1/",
            },
        },
    }

TRADE_TARIFF_CONFIG = get_trade_tariff_config

# regulation import arguments
REGULATIONS_MODEL_ARG = ["Regulation"]
REGULATIONS_DATA_PATH = APPS_DIR + "/regulations/data/{0}"
OLD_RULES_OF_ORIGIN_DATA_PATH = APPS_DIR + "/rules_of_origin/data/{0}"
RULES_OF_ORIGIN_DATA_PATH = APPS_DIR + "/rules_of_origin/ingest"
SEARCH_DATA_PATH = APPS_DIR + "/search/data/{0}"

COMMODITY_CODE_REGEX = "([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})"

# Secure cookie settings.
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

SECURE_BROWSER_XSS_FILTER = env.bool("SECURE_BROWSER_XSS_FILTER", True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("SECURE_CONTENT_TYPE_NOSNIFF", True)

LOG_LEVEL = env("LOG_LEVEL")
LOG_ECS = env.bool("LOG_ECS", True)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'ecs_formatter': {
            '()': UserLogFormatter,

            # Kibana mapping expects different types to what is sent by the library
            'exclude_fields': [
                'process',  # expects (long) but sends (object)
                'service',  # expects (string) but sends (object)
            ],
        },
        'console_formatter': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'ecs': {
            'class': 'logging.StreamHandler',
            'formatter': 'ecs_formatter',
            'stream': sys.stdout,
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console_formatter',
        },
    },
    'loggers': {
        '': {
            'level': LOG_LEVEL,
            'handlers': ['console' if not LOG_ECS else 'ecs'],
        },
    },
}


ELASTIC_APM = {
  'SERVICE_NAME': env.str('APM_SERVICE_NAME'),
  'SECRET_TOKEN': env.str('APM_SECRET_TOKEN'),
  'SERVER_URL': env.str('APM_SERVER_URL'),
  'ENVIRONMENT': env.str("APM_ENVIRONMENT"),
  'SERVER_TIMEOUT': env.str("APM_TIMEOUT"),
  'DEBUG': env.str("APM_DEBUG"),
  'ENABLED': env.str("APM_ENABLED", True),
  'RECORDING': env.str("APM_RECORDING", True),
}

SENTRY_DSN = env.str("SENTRY_DSN")
SENTRY_SECURITY_ENDPOINT = env.str("SENTRY_SECURITY_ENDPOINT", '')
SENTRY_KEY = env.str("SENTRY_KEY", '')
SENTRY_ENVIRONMENT = env.str("SENTRY_ENVIRONMENT")

SENTRY_SKIP_ENVIRONMENTS = [
    "docker-development",
]

def skip_sentry_logging(event, hint):
    if SENTRY_ENVIRONMENT in SENTRY_SKIP_ENVIRONMENTS:
        return

    return event

sentry_sdk.init(
    SENTRY_DSN,
    environment=SENTRY_ENVIRONMENT,
    integrations=[DjangoIntegration()],
    before_send=skip_sentry_logging,
)


CSP_REPORT_ONLY = env.bool("CSP_REPORT_ONLY", True)
_CSP_REPORT_URI = (
    f"{SENTRY_SECURITY_ENDPOINT}?sentry_key={SENTRY_KEY}&sentry_environment={SENTRY_ENVIRONMENT}")
CSP_REPORT_URI = (_CSP_REPORT_URI,)
_GOOGLE_DOMAINS = (
    "www.googletagmanager.com",
    "www.google-analytics.com",
    "stats.g.doubleclick.net",
    "www.google.com",
    "www.google.co.uk",
)
CSP_DEFAULT_SRC = (
    "'self'",
    *_GOOGLE_DOMAINS,
)
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",
    "'unsafe-eval'",
    *_GOOGLE_DOMAINS,
)
CSP_SCRIPT_SRC_ELEM = (
    "'self'",
    "'unsafe-inline'",
    *_GOOGLE_DOMAINS,
)
CSP_STYLE_SRC_ATTR = (
    "'self'",
    "'unsafe-inline'",
)


RESULTS_PER_PAGE = 20

DIRECTORY_FORMS_API_BASE_URL = env.str("DIRECTORY_FORMS_API_BASE_URL")
DIRECTORY_FORMS_API_API_KEY = env.str("DIRECTORY_FORMS_API_API_KEY")
DIRECTORY_FORMS_API_SENDER_ID = env.str("DIRECTORY_FORMS_API_SENDER_ID")
DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS = env(
    "DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS"
)
DIRECTORY_CLIENT_CORE_CACHE_LOG_THROTTLING_SECONDS = env(
    "DIRECTORY_CLIENT_CORE_CACHE_LOG_THROTTLING_SECONDS"
)
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT = 10

APP_START_DOMAIN = env.str("APP_START_DOMAIN")
FEEDBACK_EMAIL = env.str("FEEDBACK_EMAIL")

FEEDBACK_CONTACT = env.str("FEEDBACK_CONTACT")

DEFRA_EMAIL = env.str("DEFRA_EMAIL")
DEFRA_CONTACT = env.str("DEFRA_CONTACT")
BEIS_EMAIL = env.str("BEIS_EMAIL")
BEIS_CONTACT = env.str("BEIS_CONTACT")

DDAT_CONTACT = "DDAT Support Team"
DIT_CONTACT = "DIT EU Exit Team"

CONTACT_SUBJECT = "New UK Trade Helpdesk enquiry"
FEEDBACK_SUBJECT = "UK Trade Helpdesk feedback"
SUPPORT_SUBJECT = "UK Trade Helpdesk support request"
SERVICE_NAME = "twuk"
DIT_SUBDOMAIN = "dit"
DIT_SUBJECT_SUFFIX = " - DIT EU Exit Enquiries"
DDAT_SUBJECT_SUFFIX = " - DDAT Support Team"
HMRC_TAX_FORM_URL = env.str("HMRC_TAX_FORM_URL")

HELPDESK_GA_GTM = env.str("HELPDESK_GA_GTM")

QUOTA_DEFAULT_MESSAGE = "You can check the availability of this quota by contacting the relevant department."

EU_COUNTRY_CODES = [
    "AT",
    "BE",
    "BG",
    "HR",
    "CY",
    "CZ",
    "DK",
    "EE",
    "FI",
    "FR",
    "DE",
    "GR",
    "HU",
    "IE",
    "IT",
    "LV",
    "LT",
    "LU",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SK",
    "SI",
    "ES",
    "SE",
]

COUNTRIES_TO_REMOVE = ["XC", "XL"]
# Example:
# {
#     "EU": ["Europe (France)", "République française"],
#     "DE": ["Deutschland"],
# }
COUNTRY_SYNONYMS = {}

HIERARCHY_MODEL_MAP = {
    "Commodity": {"file_name": "prepared/commodities.json", "app_name": "commodities"},
    "Chapter": {"file_name": "prepared/chapters.json", "app_name": "hierarchy"},
    "Heading": {"file_name": "prepared/headings.json", "app_name": "hierarchy"},
    "SubHeading": {"file_name": "prepared/sub_headings.json", "app_name": "hierarchy"},
    "Section": {"file_name": "prepared/sections.json", "app_name": "hierarchy"},
}


PRIMARY_REGION = 'UK'
SECONDARY_REGION = 'EU'

MIGRATION_LINTER_OVERRIDE_MAKEMIGRATIONS = True

SUPPORTED_TRADE_SCENARIOS = (
    "ANDEAN_COUNTRIES",
    "ANDEAN_COUNTRIES_RATIFIED",
    "EU_AGR_SIGNED_LINK",
    "EU_AGR_SIGNED_NO_LINK",
    "EU_MEMBER",
    "EU_NOAGR_FOR_EXIT",
    "ONGOING_GSP_NOW",
    "ONGOING_MFN_NOW",
    "ICELAND_NORWAY",
    "JP",
    "WTO",
    "AUSTRALIA",
    "NEW_ZEALAND",
    "US",
    "CANADA",
    "CHILE",
    "MEXICO",
    "GHANA",
    "ALBANIA",
    "MONTENEGRO",
)

AGREEMENTS = [
    ("JP", True),
    ("EU", True),
]

ROO_S3_BUCKET_NAME = env.str('ROO_S3_BUCKET_NAME', '')
ROO_S3_ACCESS_KEY_ID = env.str('ROO_S3_ACCESS_KEY_ID', '')
ROO_S3_SECRET_ACCESS_KEY = env.str('ROO_S3_SECRET_ACCESS_KEY', '')

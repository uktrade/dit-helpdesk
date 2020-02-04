import os
import sys

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APPS_DIR = os.path.join(BASE_DIR, "dit_helpdesk")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "a-secret-key")

ADMIN_ENABLED = os.environ.get("ADMIN_ENABLED", "False") == "True"

# Application definition
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "formtools",
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
    "core.middleware.AdminIpRestrictionMiddleware",
    "core.middleware.NoIndexMiddleware",
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
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {"default": dj_database_url.config()}

DATA_UPLOAD_MAX_NUMBER_FIELDS = 85000  # default is 1000

CACHES = {
    "default": {"BACKEND": "redis_cache.RedisCache", "LOCATION": "localhost:6379"}
}

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
IP_SAFELIST_XFF_INDEX = int(os.environ.get("IP_SAFELIST_XFF_INDEX", "-2"))

RESTRICT_ADMIN = os.environ.get("RESTRICT_ADMIN", "True") == "True"
ALLOWED_ADMIN_IPS = os.environ.get("ALLOWED_ADMIN_IPS", "127.0.0.1").split(",")
ALLOWED_ADMIN_IP_RANGES = os.environ.get(
    "ALLOWED_ADMIN_IP_RANGES", "127.0.0.1/32"
).split(",")

# authbroker config
AUTHBROKER_URL = os.environ.get("AUTHBROKER_URL", "")
AUTHBROKER_CLIENT_ID = os.environ.get("AUTHBROKER_CLIENT_ID", "")
AUTHBROKER_CLIENT_SECRET = os.environ.get("AUTHBROKER_CLIENT_SECRET", "")

LOGIN_URL = os.environ.get("LOGIN_URL")

LOGIN_REDIRECT_URL = os.environ.get("LOGIN_REDIRECT_URL")

AUTH_USER_MODEL = "user.User"

FEEDBACK_MAX_LENGTH = 1000
CONTACT_MAX_LENGTH = 1000

# trade tariff service arguments
IMPORT_DATA_PATH = APPS_DIR + "/trade_tariff_service/import_data/{0}"
TRADE_TARIFF_SERVICE_BASE_URL = "https://www.trade-tariff.service.gov.uk/trade-tariff/"
TRADE_TARIFF_SERVICE_COMMODITIES_JSON_PATH = (
    "commodities/{0}.json?currency=EUR&day=1&month=1&year=2019"
)
TRADE_TARIFF_SERVICE_SECTION_URL = (
    "https://www.trade-tariff.service.gov.uk/trade-tariff/sections/{0}.json"
)
TRADE_TARIFF_SERVICE_MODEL_ARGS = [
    "Section",
    "Chapter",
    "Heading",
    "SubHeading",
    "Commodity",
]

# regulation import arguments
REGULATIONS_MODEL_ARG = ["Regulation"]
REGULATIONS_DATA_PATH = APPS_DIR + "/regulations/data/{0}"
RULES_OF_ORIGIN_DATA_PATH = APPS_DIR + "/rules_of_origin/data/{0}"
SEARCH_DATA_PATH = APPS_DIR + "/search/data/{0}"

TRADE_TARIFF_API = {"BASE_URL": "https://www.trade-tariff.service.gov.uk/api/v2/{0}"}

SECTION_URL = "https://www.trade-tariff.service.gov.uk/sections/{0}.json"

CHAPTER_URL = "https://www.trade-tariff.service.gov.uk/chapters/{0}.json"

HEADING_URL = "https://www.trade-tariff.service.gov.uk/headings/%s.json"

COMMODITY_URL = "https://www.trade-tariff.service.gov.uk/commodities/%s.json"

COMMODITY_CODE_REGEX = "([0-9]{4})([0-9]{2})([0-9]{2})([0-9]{2})"

# Secure cookie settings.
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

LOG_LEVEL = os.environ.get("LOGLEVEL", "info").upper()

LOGGING = {
    "version": 1,
    "handlers": {"console": {"class": "logging.StreamHandler", "stream": sys.stdout}},
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
}

sentry_sdk.init(
    os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("SENTRY_ENVIRONMENT"),
    integrations=[DjangoIntegration()],
)

RESULTS_PER_PAGE = 20

DIRECTORY_FORMS_API_BASE_URL = os.environ.get("DIRECTORY_FORMS_API_BASE_URL")
DIRECTORY_FORMS_API_API_KEY = os.environ.get("DIRECTORY_FORMS_API_API_KEY")
DIRECTORY_FORMS_API_SENDER_ID = os.environ.get("DIRECTORY_FORMS_API_SENDER_ID")
DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS = os.environ.get(
    "DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS", 0
)
DIRECTORY_CLIENT_CORE_CACHE_LOG_THROTTLING_SECONDS = os.environ.get(
    "DIRECTORY_CLIENT_CORE_CACHE_LOG_THROTTLING_SECONDS", 0
)
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT = 10

APP_START_DOMAIN = os.environ.get("APP_START_DOMAIN")
FEEDBACK_EMAIL = os.environ.get("FEEDBACK_EMAIL")

FEEDBACK_CONTACT = os.environ.get("FEEDBACK_CONTACT")

DEFRA_EMAIL = os.environ.get("DEFRA_EMAIL")
DEFRA_CONTACT = os.environ.get("DEFRA_CONTACT")
BEIS_EMAIL = os.environ.get("BEIS_EMAIL")
BEIS_CONTACT = os.environ.get("BEIS_CONTACT")

DDAT_CONTACT = "DDAT Support Team"
DIT_CONTACT = "DIT EU Exit Team"

CONTACT_SUBJECT = "New UK Trade Helpdesk enquiry"
FEEDBACK_SUBJECT = "UK Trade Helpdesk feedback"
SUPPORT_SUBJECT = "UK Trade Helpdesk support request"
SERVICE_NAME = "twuk"
DIT_SUBDOMAIN = "dit"
DIT_SUBJECT_SUFFIX = " - DIT EU Exit Enquiries"
DDAT_SUBJECT_SUFFIX = " - DDAT Support Team"
HMRC_TAX_FORM_URL = os.environ.get("HMRC_TAX_FORM_URL")

HELPDESK_GA_GTM = os.environ.get("HELPDESK_GA_GTM")

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

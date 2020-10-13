from .base import *

DEBUG = True
RESTRICT_ADMIN = False
DATABASES = {
    "default": {
        "ENGINE": "psqlextra.backend",  # 'django.db.backends.postgresql_psycopg2',
        "NAME": env.str("POSTGRES_DB"),
        "USER": env.str("POSTGRES_USER"),
        "PASSWORD": env.str("POSTGRES_PASSWORD"),
        "HOST": env.str("POSTGRES_HOST"),
        "PORT": env.str("POSTGRES_PORT"),
    }
}

REDIS_URL = "redis:6379"

CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 60 * 60 * 24,
    }
}

# Secure cookie settings.
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False

STATIC_ROOT = "dit_helpdesk/static"
INTERNAL_IPS = ["127.0.0.1", "0.0.0.0", "localhost"]

INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": show_toolbar}

ES_URL = "http://localhost:9200"

ELASTICSEARCH_DSL = {"default": {"hosts": ES_URL}}

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR + "/app-messages"

FEEDBACK_DESTINATION_EMAIL = env.str("FEEDBACK_DESTINATION_EMAIL")


HIERARCHY_MODEL_MAP = {
    "Commodity": {"file_name": "test_subsets/commodities.json", "app_name": "commodities"},
    "Chapter": {"file_name": "test_subsets/chapters.json", "app_name": "hierarchy"},
    "Heading": {"file_name": "test_subsets/headings.json", "app_name": "hierarchy"},
    "SubHeading": {"file_name": "test_subsets/sub_headings.json", "app_name": "hierarchy"},
    "Section": {"file_name": "test_subsets/sections.json", "app_name": "hierarchy"},
}
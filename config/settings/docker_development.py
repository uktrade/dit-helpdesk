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

REDIS_URL = "redis://redis:6379"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
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

ES_URL = "http://es:9200"

ELASTICSEARCH_DSL = {"default": {"hosts": ES_URL}}

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR + "/app-messages"

FEEDBACK_DESTINATION_EMAIL = env.str("FEEDBACK_DESTINATION_EMAIL")

READ_ONLY = env.bool("READ_ONLY", True)
if READ_ONLY:
    INSTALLED_APPS += ["readonly"]
    SITE_READ_ONLY = True

CMS_ENABLED = env.bool("CMS_ENABLED", False)
if CMS_ENABLED:
    INSTALLED_APPS += ["cms"]

from .base import *

DEBUG = False
RESTRICT_ADMIN = False
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
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
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

STATIC_ROOT = "dit_helpdesk/static"
INTERNAL_IPS = ["127.0.0.1", "0.0.0.0", "localhost"]

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

ROO_S3_BUCKET_NAME = env.str("ROO_S3_BUCKET_NAME", "")
ROO_S3_ACCESS_KEY_ID = env.str("ROO_S3_ACCESS_KEY_ID", "")
ROO_S3_SECRET_ACCESS_KEY = env.str("ROO_S3_SECRET_ACCESS_KEY", "")

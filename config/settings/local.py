from .base import *

DATABASES = {
    "default": {
        "ENGINE": "psqlextra.backend",  # 'django.db.backends.postgresql_psycopg2',
        "NAME": os.environ.get("DJANGO_POSTGRES_DATABASE"),
        "USER": os.environ.get("DJANGO_POSTGRES_USER"),
        "PASSWORD": os.environ.get("DJANGO_POSTGRES_PASSWORD"),
        "HOST": os.environ.get("DJANGO_POSTGRES_HOST"),
        "PORT": os.environ.get("DJANGO_POSTGRES_PORT"),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379",
        "TIMEOUT": 60 * 60 * 24,
    }
}

SECRET_KEY = env.str("DJANGO_SECRET_KEY")
RESTRICT_ADMIN = False
DEBUG = True

# Secure cookie settings.
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False

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
S3_URL = env.str("S3_URL", "")

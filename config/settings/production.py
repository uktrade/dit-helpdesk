from .base import *
from .vcap import *

assert (
    not ADMIN_ENABLED
    and env.str("DJANGO_SETTINGS_MODULE") in [
        "config.settings.production",
        "config.settings.cms_production",
    ],
)

ELASTICSEARCH_DSL = {"default": {"hosts": ES_URL}}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 60 * 60 * 24,
    }
}

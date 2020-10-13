from .base import *
import json

assert (
    not ADMIN_ENABLED
    and env.str("DJANGO_SETTINGS_MODULE") == "config.settings.production"
)

VCAP_SERVICES = json.loads(env.str("VCAP_SERVICES"))

ES_URL = VCAP_SERVICES["elasticsearch"][0]["credentials"]["uri"]

ELASTICSEARCH_DSL = {"default": {"hosts": ES_URL}}

REDIS_URL = VCAP_SERVICES["redis"][0]["credentials"]["uri"]

CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 60 * 60 * 24,
    }
}

from .base import *
from .vcap import *

ELASTICSEARCH_DSL = {"default": {"hosts": ES_URL}}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 60 * 60 * 24,
    }
}

TRADE_TARIFF_CONFIG = env.json("TRADE_TARIFF_CONFIG", TRADE_TARIFF_CONFIG)

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

    def show_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": show_toolbar}

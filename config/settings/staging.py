from .base import *
import json

ADMIN_ENABLED = False

VCAP_SERVICES = json.loads(os.environ.get('VCAP_SERVICES', {}))

ES_URL = VCAP_SERVICES['elasticsearch'][0]['credentials']['uri']

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': ES_URL
    }
}

REDIS_URL = VCAP_SERVICES['redis'][0]['credentials']['uri']

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
    }
}
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

    def show_toolbar(request):
        return True

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': show_toolbar,
    }

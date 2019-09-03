from .base import *

DEBUG = True
RESTRICT_ADMIN = False
DATABASES = {
    'default': {
        'ENGINE': 'psqlextra.backend',  # 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DJANGO_POSTGRES_DATABASE'),
        'USER': os.environ.get('DJANGO_POSTGRES_USER'),
        'PASSWORD': os.environ.get('DJANGO_POSTGRES_PASSWORD'),
        'HOST': os.environ.get('DJANGO_POSTGRES_HOST'),
        'PORT': os.environ.get('DJANGO_POSTGRES_PORT')
    }
}

# Secure cookie settings.
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False

STATIC_ROOT = 'dit_helpdesk/static'
INTERNAL_IPS = ['127.0.0.1', '0.0.0.0', 'localhost']

INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}

ES_URL = 'http://es:9200'

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': ES_URL
    },
}

DIRECTORY_FORMS_API_BASE_URL=os.environ.get('DIRECTORY_FORMS_API_BASE_URL')
DIRECTORY_FORMS_API_API_KEY=os.environ.get('DIRECTORY_FORMS_API_API_KEY')
DIRECTORY_FORMS_API_SENDER_ID=os.environ.get('DIRECTORY_FORMS_API_SENDER_ID')
DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS=os.environ.get('DIRECTORY_CLIENT_CORE_CACHE_EXPIRE_SECONDS', 0)
DIRECTORY_CLIENT_CORE_CACHE_LOG_THROTTLING_SECONDS=os.environ.get('DIRECTORY_CLIENT_CORE_CACHE_LOG_THROTTLING_SECONDS', 0)
DIRECTORY_FORMS_API_DEFAULT_TIMEOUT=0
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

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR+'/app-messages'

FEEDBACK_DESTINATION_EMAIL = os.environ.get('FEEDBACK_DESTINATION_EMAIL')

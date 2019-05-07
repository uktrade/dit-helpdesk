from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'psqlextra.backend',  # 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DJANGO_POSTGRES_DATABASE'),
        'USER': os.environ.get('DJANGO_POSTGRES_USER'),
        'PASSWORD': os.environ.get('DJANGO_POSTGRES_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'a-secret-key')
RESTRICT_ADMIN = False
DEBUG = True

# Secure cookie settings.
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False

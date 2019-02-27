from .base import *

import dj_database_url


DATABASES = {
   'default': dj_database_url.config()
}

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DEBUG = False

"""
DATABASES = {
    'default': {
        'ENGINE': 'psqlextra.backend',  # 'django.db.backends.postgresql_psycopg2',
        'NAME': 'tradehelpdesk2',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
"""

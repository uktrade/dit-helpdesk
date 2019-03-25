from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'psqlextra.backend',  # 'django.db.backends.postgresql_psycopg2',
        'NAME': 'helpdesk2',
        'USER': 'ldluser',
        'PASSWORD': 'ldluser',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
SECRET_KEY=os.environ.get('DJANGO_SECRET_KEY', 'a-secret-key')
RESTRICT_ADMIN = False
DEBUG=True

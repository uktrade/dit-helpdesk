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
SECRET_KEY="""SiMh\'&+z^q+xJi|a^f]cnxK#@RtB76aud"1pwCUO;8.GVY"""
RESTRICT_ADMIN = False
DEBUG=True
ALLOWED_HOSTS = ['0.0.0.0', '192.168.71.100']
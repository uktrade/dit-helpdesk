web: python manage.py collectstatic -l --noinput && gunicorn --worker-class=gevent --worker-connections=1000 --workers 9 config.wsgi:application --bind 0.0.0.0:$PORT

web: python manage.py collectstatic -l --noinput && python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT

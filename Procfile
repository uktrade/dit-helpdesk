web: cd dit_helpdesk && python manage.py collectstatic -l --noinput && python manage.py migrate && gunicorn dit_helpdesk.wsgi:application --bind 0.0.0.0:$PORT

web: cd dit_helpdesk && python3 manage.py collectstatic -l --noinput && python3 manage.py migrate && gunicorn dit_helpdesk.wsgi:application --bind 0.0.0.0:$PORT

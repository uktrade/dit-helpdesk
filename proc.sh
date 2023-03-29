#!/bin/bash
python manage.py collectstatic -l --noinput
if [ $? -ne 0 ]; then
    exit
fi

if [ "$RUN_MIGRATIONS" ]; then
    python manage.py migrate
fi

if [ $? -ne 0 ]; then
    exit
fi

# gunicorn -c config/gunicorn.py config.wsgi:application --worker-class=gevent --worker-connections=1000 --workers 9 --bind 0.0.0.0:$PORT
gunicorn -c config/gunicorn.py config.wsgi:application --bind 0.0.0.0:$PORT
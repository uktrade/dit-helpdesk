set -e

python manage.py lintmigrations --exclude-apps flags

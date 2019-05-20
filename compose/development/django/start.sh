#!/bin/bash -xe
# pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py loaddata countries_data
python manage.py scrape_section_hierarchy_v2
python manage.py import_rules_of_origin --data_path "import"
python manage.py import_regulations
#sleep infinity
python manage.py runserver_plus 0.0.0.0:8000

echo "docker exec -it dit_helpdesk_helpdesk_1 /bin/bash"
echo "python manage.py scrape_section_hierarchy_v2"
#python manage.py scrape_section_hierarchy_v2

# -----------------------------------------------------------------------------
# To destroy and rebuild:
# -----------------------------------------------------------------------------
# $ docker-compose stop
# $ docker-compose rm
# $ docker-compose build
# $ docker-compose up
# -----------------------------------------------------------------------------

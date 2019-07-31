#!/bin/bash -xe
# pip install -r requirements/development.txt
#python manage.py collectstatic --noinput
#python manage.py migrate
#python manage.py loaddata countries_data
#python manage.py pull_api_update
#python manage.py prepare_import_data
#python manage.py scrape_section_hierarchy
#python manage.py import_rules_of_origin --data_path "import"
#python manage.py import_regulations
#python manage.py import_search_keywords -f output/commodity_category_all_with_synonyms_greenpage.csv
#TODO:
#make debug
#make debug_webserver
#make debug_test

sleep infinity
#python manage.py runserver_plus 0.0.0.0:8000
#python manage.py runserver 0.0.0.0:8000

echo "docker exec -it dit_helpdesk_helpdesk_1 /bin/bash"
echo "python manage.py scrape_section_hierarchy"
#python manage.py scrape_section_hierarchy

# -----------------------------------------------------------------------------
# To destroy and rebuild:
# -----------------------------------------------------------------------------
# $ docker-compose stop
# $ docker-compose rm
# $ docker-compose build
# $ docker-compose up
# -----------------------------------------------------------------------------

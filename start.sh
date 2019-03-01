#!/bin/bash -xe
python dit_helpdesk/manage.py collectstatic --noinput
python dit_helpdesk/manage.py migrate
python dit_helpdesk/manage.py loaddata countries_data
npm install
npm rebuild node-sass
npm run build
# sleep infinity
python dit_helpdesk/manage.py runserver_plus 0.0.0.0:8000

echo "docker exec -it dit-helpdesk_helpdesk_1 /bin/bash"
echo "python dit_helpdesk/manage.py scrape_section_hierarchy 1"

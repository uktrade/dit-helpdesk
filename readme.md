# DIT Helpdesk

This service is used to help people find the correct Harmonised System (HS) code, duties, rules of origin etc for the
products that they want to export to the UK.


## Requirements
 - Python 3
 - Node [Active LTS][1] version (Current Active version is v10)
 - Docker (if developing locally with docker)

 #### Optional. Only required for testing contact form submissions to zenddesk
 - Directory Forms API (https://github.com/uktrade/directory-forms-api)
    - redis (installed locally)
    - postgres (installed locally)

### Install using Docker

If you have Docker installed, you can run this service without needing to set up the database yourself, worrying about
virtual environments - it's all within the Docker instance.

- Docker for mac - https://hub.docker.com/editions/community/docker-ce-desktop-mac
- Docker for Win - https://download.docker.com/win/static/stable/x86_64/

## Installation

### Directory Forms API (Optional only required when testing contact form submissions to zenddesk)


clone the directory
```
git clone https://github.com/uktrade/directory-forms-api.git .
```

create a hosts file entry for

`127.0.0.1    forms.trade.great`
=======

Follow installation and setup instructions in https://github.com/uktrade/directory-forms-api/blob/develop/README.md

NB: add the following entries to the env file

```
HEALTH_CHECK_TOKEN=""
DEFAULT_FROM_EMAIL=""
REDIS_CELERY_URL="redis://localhost:6379"
GOV_NOTIFY_LETTER_API_KEY=debug
DJANGO_SECRET_KEY=debug
FEATURE_ENFORCE_STAFF_SSO_ENABLED=False
STAFF_SSO_AUTHBROKER_URL=
AUTHBROKER_CLIENT_ID=
AUTHBROKER_CLIENT_SECRET=
```
after running `make debug` in a terminal

create a superuser by running the following in a terminal

```
export DATABASE_URL=postgres://debug:debug@localhost:5432/directory_forms_api_debug
./manage.py createsuperuser
```

then run `make debug_webserver` to start the server

access the application admin screens locally in you browser with the url http://forms.trade.great:8011/admin

Click the add button in the Client section and add `helpdesk` as the name of the client then click submit. This will
generate the user identifier and accss key that you need to add to the .env file for the `dit_helpdesk` application

** ToDo: incorporate into docker as service

### UK Trade Helpdesk
First clone the repo

```bash
git@github.com:uktrade/dit-helpdesk.git .

```

then using a terminal move inside of the folder:

```bash
cd dit-helpdesk
```

#### Frontend static asset installation

First we need to install [GOV.UK Frontend][2] and
[GOV.UK country and territory autocomplete][3] (Which will also also install the required [Accessible Autocomplete][4]
dependency), and other front end dependencies.

This is all done by going to the project root folder, which contains `package.json`. Then run:

```bash
npm install
```

This will install all of the packages needed to build the front end static assets.

To build and move all of the static assets:

```bash
npm run build
```

`npm run` will show a list of all of the commands available, including linting.

#### set environment variables

copy the two development environment variables files

```
cp .env.template .env
cp .env.template .env.test

```

add entries where necessary (see comments for guidance)

You will need to access [Helpdesk Vault][5] to get the required environment variable secrets to use them in the file.
To do so you will need to generate a github personal access token. This is needed to log into vault.
Go here: [Vault][6] click `Generate new token` and make sure it has these scopes: `read:org`, `read:user`.
Once you've done that, head over to [Vault][7] and login with the token. You'll need to select github
as your login option.

#### Install for development with Docker

Make sure that Docker is installed and running.

##### Initial setup run

This intial set up will take about an hour (depending upon machine and internet speed) to set up and fully import
all content, on subsequent runs it will on take a minute or so to be up and running for development.

The initial run (this section) only needs to be done when building a new or fresh docker container. Once this section
has been done and as long as the docker images are not destroyed, the only line that needs to be uncommented
when running`docker-compose -f development.yml up` will be.

NOTE: On first setup if you don't have the [Directory Forms API](https://github.com/uktrade/directory-forms-api/blob/develop/README.md) docker environment running you may receive the error:

    ERROR: Network directory-forms-api_outside-network declared as external, but could not be found. Please create the network manually using `docker network create directory-forms-api_outside-network` and try again.

You can either run the docker environment for Directory Forms API, which will create this network for you or create it manually using the command it gives.

This section details manually running each command in turn to fuly import all content.

NB: Alternatively, you can comment out `sleep infinity` and uncomment those that are commented, below, and the entire
process should run automatically on `docker-compose -f development.yml up`, ending with a running application accessible
at http://localhost:8000/choose-country/

```
python manage.py runserver_plus 0.0.0.0:8000
```

Open `compose/development/django/start.sh` and make sure the commands
of the Initialize section are commented as below

```
    # ----------------- commands ----------------
    sleep infinity
    # python manage.py collectstatic --noinput
    # python manage.py migrate
    # python manage.py loaddata countries_data
    # python manage.py pull_api_update
    # python manage.py prepare_import_data
    # python manage.py scrape_section_hierarchy
    # python manage.py import_rules_of_origin --data_path "import"
    # python manage.py import_regulations
    # python manage.py import_search_keywords -f output/commodity_category_all_with_synonyms_greenpage.csv
    # python manage.py search_index --populate
```

make sure the commands of the Ongoing Development section are commented as below

```
    # ----------------- commands ----------------
    #python manage.py runserver_plus 0.0.0.0:8000
```

To build the docker containers, run:

```bash
docker-compose -f development.yml build
```

To run the Docker containers, run:

```bash
docker-compose -f development.yml up
```

Open a second terminal and run the following command to activate a shell into the docker instance
for the trade helpdesk app with the command.

```
docker exec -it dit_helpdesk_helpdesk_1 /bin/bash
```
NB: if `dit_helpdesk_helpdesk_1` is not found run `docker ps` in your host terminal to get a list of the docker images
and their correct names

refer to "Running, then shelling in" section below

In the docker shell Run the following collect static files and migrate the database schema and
create the countries content

```
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py loaddata countries_data
```

Whilst still in the docker shell, run the following commands to collect the hierarchy content from the trade tariff API
and prepare it for import into the django database, then import

** todo: rename scrape_section_hierarchy

###### Commodities and Hierarchy
To populate the commodities in the database, we need to:
- pull data from the api,
- prepare the api data for import
- import the data.

to do this we run a set of management commands:
```
python manage.py pull_api_update
python manage.py prepare_import_data
python manage.py scrape_section_hierarchy
```
This should take approximately 10 to 15 minutes

###### Rules of Origin
run the following command to import the Rules of origin documents

```
python manage.py import_rules_of_origin --data_path "import"
```

This should take approximately a couple of minutes

NB: see `Extracting Rules of Origin data from word documents ready for import` below to recreate reuls of origin data
or add new rules

###### Documents and regulations
The source data for this content should be in a json format.
run the following command to import the regulations content
```
python manage.py import_regulations
```
This should take approximately 10 minutes.


run the following command to import search keywords into the the hierarchy items

```
python manage.py import_search_keywords -f output/commodity_category_all_with_synonyms_greenpage.csv
```

run the following command to create the elasticsearch indexes

```
python manage.py search_index --create
python manage.py search_index --populate
```

Note: See below for more details including generating data to import files and clearing the database

When finished this process in a new host shell (not the docker shell, nor the host shell currently running the docker
containers) run the following to shut down (not destroy) the running docker instance.

```
docker-compose -f development.yml stop
```
### Ongoing Developement with Docker

make sure that in the file `compose/development/django/start.sh` the only command uncommented is

```
python manage.py runserver_plus 0.0.0.0:8000
```

the rest of the commands should be commented out

** todo: make the process of running intial set up and running developement set up less cumbersome

Starting the server again is the same command as installing:

```bash
docker-compose -f development.yml up
```

The site will be available at http://localhost:8000/choose-country/

To trigger a build when any Sass is changed, run the following command in the root of the project folder in a
`host machine` shell, not a `docker instance` shell:
```bash
npm run watch:styles
```

### Running, then shelling in

If you want to be able to run commands in bash within the docker instance, we need to change the start
script `compose/development/django/start.sh` slightly.

stop the docker instance

```
docker-compose -f development.yml stop
```

NB: do not use `docker-compose -f development.yml down` as that will stop the containers and delete the images and
you will need ot go through the whole intial process of building and setting up with content again.

Uncomment the sleep command:
```
sleep infinity
```
and comment out the line that starts the app,
```
# python dit_helpdesk/manage.py runserver_plus 0.0.0.0:8000
```

This will cause the docker instance to pause once it's up and running.

```
docker-compose up
```
then enter a shell for the docker instance of the django service

```
docker exec -it dit-helpdesk_helpdesk_1 /bin/bash
```
and for database access the postgres service
```
docker exec -it dit-helpdesk_postgres_1 /bin/bash
```

### Extracting Rules of Origin data from word documents ready for import
There is a management command for extracting data from word documents that may be supplied for new content,
from time to time. First, place the new word documents in the `rules_of_origin/data/source`folder then run the
`scrape_rules_of_origin_docx`data extraction command. The command will generate json files in the
`rules_of_origin/import_folder`where the importer command will read them from.
Be sure to archive any existing word files and/or json files should there be anyone clear the two folders.
To extract data from word docx source content, run:
```bash
python dit_helpdesk/manage.py scrape_rules_of_origin_docx
```
This should take a couple of minutes per word document.

### Preparing the regulations content

### Preparing the search indexes

### Workaround for creating superuser for admin in development

Make sure that you have the correct settings values for the authbroker sso integration

If these have been set up on PaaS check either the vault or `cf env {yourapp}` for appropriate values. If they have not
been set up check with system administrator.

Use to django management command to get into an environment shell on you local development environment

```
./manage.py shell_plus

```

Then create the super user like so:

```
from django.contrib.auth import get_user_model

user = get_user_model().objects.get(email='<<your gov.uk email address>>')
user.is_superuser=True
user.is_staff=True
user.save()
```

### Running tests with Docker development deployment

refer to the section `Running, then shelling in` above to get a shell in the runnig docker instance

From within the docker shell terminal run the following command for full tests:
```
coverage run manage.py test dit_helpdesk --settings=config.settings.test
```
for testing a single app run i.e. the hierarchy app:
```
coverage run manage.py test hierarchy.tests --settings=config.settings.test
```
for testing a single app's test module run i.e. the test_views in the the hierarchy app:
```
coverage run manage.py test hierarchy.tests.test_views --settings=config.settings.test
```
and so on.

for coverage reports run

```
coverage -d reports html
```
you will then be able to access the coverage report html from within your project folder's root
from your host machine at /reports


### Running tests and generating coverage with Docker

```bash
docker-compose -f text.yml build
docker-compose -f test.yml up

```

This will display in the shell the following:
- all tests, showing passes and failures
- coverage report

it will also generate the following reports into folder `reports` :
- xunit coverage report file
- xml coverage report file
- html coverage report

## Country synonyms

The list of all countries that need to be listed is in `assets/countries/countries-data.json`. If the countries and/or
synonyms need to be updated, change the `countries-data.json` to add countries; and change `add-synonyms.js` file to
add synonyms. Then run `npm run update-countries`. You should see the updated
files in `dit_helpdesk/static_collected/js/`.


### Install locally

To run, we need to create a Python virtual environment and install any requirements.

## Requirements
 - Python 3
 - Node [Active LTS][8] version (Current Active version is v10)
 - postgresql

When in the project folder, create a virtual environment.

```bash
python3 -m venv venv/
```

Now activate the virtual environment:

```bash
source venv/bin/activate
```

If the virtual environment has been activated correctly your terminal should have `(venv)` at the start - for example:

```bash
(venv) computer:folder username$
```

With the virtual environment working, we can now install everything this project needs using Python's package manager `pip`:

```bash
pip install -r requirements/local.txt
```

Once that's done, we now have to configure the development set up. `cd` into `dit_helpdesk`, then run these three commands:

```bash
export PYTHONPATH=$(pwd)
```

```bash
export DJANGO_BASE_DIR=$(pwd)
```

```bash
export DJANGO_SETTINGS_MODULE=dit_helpdesk.settings.local
```

To populate the products in the database, we need to run a scrape. To get the products in Section I, run:

```bash
python manage.py scrape_section_hierarchy 1
```

To get Section II, replace 1 with 2; Section III, use 3 - and so on. Recommend scraping at least one section. The scrape will take a while.

Now we need to [build the front end static assets][9].

Once the scraping has finished and the front end assets are in place, start the server:

```bash
python manage.py runserver
```

## Appendices

### Appendix I - Frontend Notes

The source for the static assets is in `assets` in the root of the project folder. This contains the Sass files that the CSS is generated from, and the source of the client-side JavaScript.

All of the dependencies have been compiled and are included in the git repository because the Jenkins build process that deploys the site doesn't run Node. This means that you won’t need to build the CSS and JavaScript unless you change anything. Any changes should be tested before merging into the master branch, so this should help ensure that any frontend problems are not during the Jenkins build process.

Before changing anything, make sure that the dependencies are installed. Once that’s done,
```bash
npm run build
```
will run the process that builds the CSS and JavaScript.

Not all of GOV.UK Frontend is included, since this service doesn’t use all of the components. The components that aren’t being used are commented out in `global.scss` - when editing them, remember to re-run

```bash
npm run build
```
to build the styles.

GOV.UK Frontend CSS is namespaced with `govuk-` at the start of every class name. The namespace for Sass specific to this service is `app-`. All of the `app-` Sass is in the `assets/scss` folder. See the Design System team’s guidance on Extending and modifying components in production for building on top of GOV.UK Frontend.

If things are looking broken, first run
```bash
npm run build
```
this will rebuild and recompile all of the frontend static assets.

If the country autocomplete is not working, first:  open up the browser console to see if there are any error messages - it could be anything from a 404 file not found to a script loaded by Google Tag Manager clashing with existing JavaScript

If the country autocomplete is blank:

Turn off JavaScript in your browser, visit the choose country page (`/choose-country`) and see if a <select> dropdown is there
If a select is not present, then the problem is in the template file - look at `dit_helpdesk/countries/templates/countries/choose_country.html` to see why it’s been left out
If the select is empty, or has an incomplete list of countries, then the problem is on the server-side list of countries. On the server, run

```bash
python dit_helpdesk/manage.py loaddata countries_data
```

to repopulate the list of countries.

If the select is present, but the autocomplete isn’t working:

```bash
Run `npm run build`
Run `npm run update-countries`
Run `python dit_helpdesk/manage.py loaddata countries_data`
```

If the autocomplete is not using the correct synonyms:
Open `assets/countries/add-synonyms.js` and check that the `countriesToAddSynonymsTo` array of objects is correct.
If any corrections are needed, make them - then run

```bash
npm run build
```

followed by

```bash
npm run update-countries
```

and then

```bash
python dit_helpdesk/manage.py loaddata countries_data
```

If the autocomplete is not displaying properly run

```bash
npm run build
```

The autocomplete is set up to enhance a select - check that the `id` of the select element and in the JavaScript match up. These are in `dit_helpdesk/countries/templates/choose_country.html`


Check that `assets/scss/global.scss` has an `@import` for `govuk-country-and-territory-autocomplete/dist/location-autocomplete.min`. If not, add in `@import "govuk-country-and-territory-autocomplete/dist/location-autocomplete.min";` and re-run

```bash
npm run build
```

### Apendix II - Management Import Commands

### Countries


The project has a django fixtures file for populating the countries database table with country code and name values

These would normally be imported on deployment, however, in the case where countries need to be added to the

```bash
countries/fixtures/countries.json
```

file they can be reloaed with the command:

```bash
python dit_helpdesk/manage.py loaddata countries_data
```

### Commodity Hierarchy


#### Importing Commodity Hierarchy Data


To import commodity hierarchy content run:

```bash
python dit_helpdesk/manage.py scrape_section_hierarchy
```

The main python class used by this command can be found in the python module `trade_tarrif_service/importer.py`

The source data for this command can be found in the directory `trade_tarrif_service/import_data`


#### Generating Commodity Hierarchy Data for Import

The json files that are generated from the tarrifs project database are placed in the directory`trade_tarrif_service/import_data`

This include the data files for Chapters, Headings, SubHeadings and Commodities

There is a method in the class that collects the section data from the trade tariff api and generates a json file.

Use this in the case where the sections data needs to be refreshed before import of the hierarchy:

```bash
python dit_helpdesk/manage.py scrape_section_json
```

This command uses a method `get_section_data_from_api()` of the main python class found in the python module `trade_tarrif_service/importer.py`

#### Clearing the Data from the Database

To clear the data from the database before re-importing use the following sql statement in a psql shell:

```sql
truncate table hierarchy_section CASCADE;
```

This Cascades to tables:

* regulations_regulation_commodities
* regulations_regulation_sections
* regulations_document_regulations
* regulations_regulation_chapters
* regulations_regulation_headings
* regulations_regulation_subheadings

### Rules of Origins Documents

Each commodity has an associated list of rules of origin data which we need to generate from source dcouments
and import into the database.

#### Generating Rules of Origin Data

New rules of origin documents get placed in the directory `rules_of_origin/data/source`

To process all rules of origin documents use:

```bash
python dit_helpdesk/manage.py scrape_rules_of_origin_docx --data_path source
```

To import an individual rules of origin data file use:

```bash
python dit_helpdesk/manage.py scrape_rules_of_origin_docx --data_path "source/Chile ROO v2.docx"
```

The main python class used by this command can be found in the python module `rules_of_origin/ms_word_docx_scraper.py`


#### Importing Rules of Origin Data


Rules of origin data generated for import get placed in the directory `rules_of_origin/data/import`

To import all rules of origin data files use:

```bash
python dit_helpdesk/manage.py import_rules_of_origin --data_path import
```

To import an individual rules of origin data file use:

```bash
python dit_helpdesk/manage.py import_rules_of_origin --data_path "import/CHILE ROO V2.json"
```

The main python class used by this command can be found in the python module `rules_of_origin/importer.py`

#### Clearing the Data from the Database

To clear the data from the database before re-importing use the following sql statement in a psql shell:

```sql
truncate table rules_of_origin_rulesgroup CASCADE;
```

This cascades to tables:

* rules_of_origin_rulesdocument
* rules_of_origin_rulesgroupmember
* rules_of_origin_rule
* rules_of_origin_rulesdocumentfootnote


### Regulations and Documents

Each commodity has an associated list of regulations which we need to fetch and populate the database.

Regulations and documents data gets placed in the directory `regulations/data`

#### Generating Regulations and Documents data

To get the regaulation documents titles for the supplied document urls run:

```bash
python dit_helpdesk/manage.py scrape_documents
```

The source file is `product_specific_regulations.csv`

The output file is `urls_with_text_description.json`

#### Importing Regulations and Documents

To import the regulations and documents data into the database run:

```bash
python dit_helpdesk/manage.py import_regulations
```

#### Clearing the Data from the Database

To clear the data from the database before re-importing use the following sql statement in a psql shell:

```sql
truncate table regulations_document CASCADE;
truncate table regulations_regulation CASCADE;
```

This cascades to tables:

* regulations_regulation_commodities
* regulations_regulation_sections
* regulations_document_regulations
* regulations_regulation_chapters
* regulations_regulation_headings
* regulations_regulation_subheadings


[1]:	https://nodejs.org/en/about/releases/
[2]:	https://github.com/alphagov/govuk-frontend
[3]:	https://github.com/alphagov/govuk-country-and-territory-autocomplete
[4]:	https://github.com/alphagov/accessible-autocomplete
[5]:	%60https://vault.ci.uktrade.io/ui/vault/secrets/dit%2Ftrade-helpdesk/list/helpdesk/%60
[6]:	%60https://github.com/settings/tokens%60
[7]:	%60https://vault.ci.uktrade.io%60
[8]:	https://nodejs.org/en/about/releases/
[9]:	#frontend-build

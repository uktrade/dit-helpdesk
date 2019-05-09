# DIT Helpdesk

This service is used to help people find the correct Harmonised System (HS) code, duties, rules of origin etc for the 
products that they want to export to the UK.


## Requirements
 - Python 3
 - Node [Active LTS][1] version (Current Active version is v10)
 - Docker (if developing locally with docker)

## Installation

First clone the repo

```bash
git@github.com:uktrade/dit-helpdesk.git . 

``` 

then using a terminal move inside of the folder:

```bash
cd dit-helpdesk
```

### Install using Docker

If you have Docker installed, you can run this service without needing to set up the database yourself, worrying about 
virtual environments - it's all within the Docker instance.

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

#### Install for development with Docker

Make sure that Docker is installed and running. Open `start.sh` and comment back to the terminal

Then run:

```bash
docker-compose -f development.yml build
```

Once the build has completed, comment out the pip installation in `start.sh` - this isn't essential, but it will 
save you time when booting up the docker instance.

Now run:

```bash
docker-compose -f development.yml up
```

The `start.sh` script will run the following django management commands 

```bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py loaddata countries_data
python manage.py scrape_section_hierarchy
python manage.py import_rules_of_origin --data_path "import"
python manage.py import_regulations
python manage.py runserver_plus 0.0.0.0:8000

```
`scrape_section_hierarchy` will only run if there are no Sections items found. see below if you need to run this 
manually `import_rules_of_origin` and `import_regulations` will create any new items that do not already exist.
you can comment these three lines out after the initial out `up` to speed up the buid and deploy process locally.
The last line starts the django server

##### Preparing to Manually Install content
If you need to populate the database with products. 

first commenting out 
```bash
python manage.py scrape_section_hierarchy
python manage.py import_rules_of_origin --data_path "import"
python manage.py import_regulations
```

refer to "Running, then shelling in" section below

##### Manually Install content
Once into the command prompt in the terminal you should now be in the root of the app. 

Note: See below for more details including generating data import files and clearing the database

###### Commodities and Hierarchy
To populate the commodities in the database, we need to run a management command to import the data. 
To import the commodity data and its hierarchy, run:

```bash
python dit_helpdesk/manage.py scrape_section_hierarchy
```
This should take approximately 6 to 8 minutes
###### Rules of Origin
To import Rules of Origin run:
```bash
python dit_helpdesk/manage.py import_rules_of_origin
```
This should take approximately 1 minutes 

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

###### Documents and Regulations
The source data for this content should be in a json format. #TODO: add detail here
To import Documents and regulations run:
```bash
python dit_helpdesk/manage.py import_regulations
```
This should take approximately 60 minutes. (#TODO: redo the code to reduce this time.

##### Update Environment variables in case you get Sentry exceptions (Optional)
If `docker-compose.env` file does not exists, create it by copying `docker-compose.conf.env`

You will need to access [Helpdesk Vault][5] to get the required environment variable secrets to use them in the file. 
To do so you will need to generate a github personal access token. This is needed to log into vault. 
Go here: [Vault][6] click `Generate new token` and make sure it has these scopes: `read:org`, `read:user`. 
Once you've done that, head over to [Vault][7] and login with the token. You'll need to select github 
as your login option.

### Running developement with Docker
Starting the server again is the same command as installing:

```bash
docker-compose -f development.yml up
```

The site will be available at http://localhost:8000/choose-country/.

To trigger a build when any Sass is changed, run:
```bash
npm run watch:styles
```

### Running, then shelling in

If you want to be able to run commands in bash within the docker instance, we need to change the start 
script `start.sh` slightly.

Comment out the line that starts the app, and comment back in the sleep command. So it should read:
```bash
sleep infinity
# python dit_helpdesk/manage.py runserver_plus 0.0.0.0:8000
```

This will cause the docker instance to pause once it's up and running. Now

```bash
docker-compose up
```
then

```bash
docker exec -it dit-helpdesk_helpdesk_1 /bin/bash
```

### Running tests with Docker development deployment

In th first terminal run: 
```bash
docker-compose -f development.yml build
docker-compose -f development.yml up
```

open a new terminal and run:
```bash
docker-compose -f development.yml run -e DJANGO_SETTINGS_MODULE=config.settings.test \
    --no-deps --rm helpdesk \
    coverage run manage.py test dit_helpdesk --noinput
```
This will run all tests and display the output in the terminal.

NB: Although we are not displaying the coverage report, we use coverage to run the test here because there is an issue with
reporting coverage of django models using noestest runner without starting the test process with coverage  

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

## Appendix - Frontend Notes

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

## Management Import Commands


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
<<<<<<< HEAD
python dit_helpdesk/manage.py scrape_section_hierarchy
=======
python dit_helpdesk/manage.py scrape_section_hierarchy_v2
>>>>>>> updated readme
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
python dit_helpdesk/manage.py import_rules_or_origin --data_path import
```

To import an individual rules of origin data file use:
```bash
python dit_helpdesk/manage.py import_rules_or_origin --data_path "import/CHILE ROO V2.json"
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

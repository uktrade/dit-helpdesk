# DIT Helpdesk

This service is used to help people find the correct Harmonised System (HS) code, duties, rules of origin etc for the
products that they want to export to the UK.

## Requirements

### Without Docker

- Python 3
- Node [Active LTS][1] version (Current Active version is v14)

#### Optional. Only required for testing contact form submissions to zenddesk

- Directory Forms API (https://github.com/uktrade/directory-forms-api)
  - redis (installed locally)
  - postgres (installed locally)

### With Docker (recommended)

If you have Docker installed, you can run this service without needing to set up the database yourself or worrying about
virtual environments - it's all within the Docker instance.

- Docker for mac - https://hub.docker.com/editions/community/docker-ce-desktop-mac
- Docker for Win - https://download.docker.com/win/static/stable/x86_64/

## Installation

### UK Trade Helpdesk

First clone the repo

```bash
git clone git@github.com:uktrade/dit-helpdesk.git

```

then using a terminal move inside of the folder:

```bash
cd dit-helpdesk
```

#### set environment variables

Copy the two development environment variables files:

```
cp .env.template .env
cp .env.template .env.test

```

and add entries where necessary (see comments for guidance).
It may be easier to create one of the files and fill in the values, then copy that to create the second file.

You will need to access [Helpdesk Vault][5] to get the required environment variable secrets to use them in the file.
To do so you will need to generate a github personal access token. This is needed to log into vault.
Go here: [Vault][6] click `Generate new token` and make sure it has these scopes: `read:org`, `read:user`.
Once you've done that, head over to [Vault][7] and login with the token. You'll need to select github
as your login option.

The values
  * `HELPDESK_GA_GTM`
  * `HELPDESK_GA_UA`
  * `DEFRA_EMAIL`
  * `DEFRA_CONTACT`
  * `BEIS_EMAIL`
  * `BEIS_CONTACT`

are not present in Vault, but the local environment will work without them.

The value for `POSTGRES_PASSWORD` is also not present in Vault. You can provide your own value for this.

#### pre-commit

Install the pre-commit hook which will execute Python and JS code formatters before commit.

(If you do not already have the `pre-commit` command installed, follow the directions at https://pre-commit.com/)

```bash
pre-commit install
```

#### Install for development with Docker (recommended)

Make sure that Docker is installed and running.

```bash
docker-compose up -d
```

##### Initial setup run

This initial setup will take about an hour (depending upon machine and internet speed) to set up and fully import
all content. On subsequent runs it will on take a minute or so to be up and running for development.

Before starting setup, download the required Rules of Origin files by following the instructions given below
in [the section on the `import_rules_of_origin` management command](#import_rules_of_origin).

Run the following commands to activate a shell into the docker instance for the trade helpdesk app with the command.

```bash
docker-compose exec helpdesk /bin/bash
```

```bash
pipenv shell
./manage.py migrate
./reload_data.sh
```

The site will be available at http://localhost:8000/choose-country/

There may be a short delay before the site is available as the `helpdesk` container waits for the
ElaticSearch container `es` to complete initialisation. The command
```bash
docker-compose logs helpdesk | grep 'Development server is running'
```
will return success when the web server has started (until the logs are rotated).

###### Ignorable errors

You may see messages mentioning `NewConnectionError` while the `reload_data` script runs. These can be ignored.

When a management command (including `reload_data`) completes successfully, you may see an error message that
`Closing the transport connection timed out`. This can be ignored.

##### Possible error: "Found missing descriptions in…"

The setup process may fail in the `prepare_import_data` step with the error "Found missing descriptions in [UK or EU]".
Steps for resolving this are described below in
[the section on the `prepare_import_data` management command](#error-commodity-found-with-no-description).

#### Non-Docker installation

##### External services

You will need to have the following installed:

  - Postgres
  - Elasticsearch
  - Redis

##### Frontend static asset installation

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

##### Python installation

You will need to install pipenv

```bash
pip install pipenv
```

Then install the required dependencies

```bash
pipenv install --dev
```

Then the init script can be run via

```bash
pipenv shell
./reload_data.sh
```

### Directory Forms API (Optional only required when testing contact form submissions to zenddesk)

clone the directory

```
git clone https://github.com/uktrade/directory-forms-api.git .
```

Follow installation and setup instructions in https://github.com/uktrade/directory-forms-api/blob/develop/README.md to get the directory forms API running locally and to create a superuser.

Access the application admin screens locally in you browser with the url http://localhost:8011/admin.

Click the add button in the Client section and add `helpdesk` as the name of the client then click submit. This will
generate the user identifier and access key that you need to add to the .env file `DIRECTORY_FORMS_API_*` variables for the `dit_helpdesk` application.

### Running tests with Docker

To run the tests in the Docker environment shell into the running container:

```bash
docker-compose exec helpdesk /bin/bash
pipenv shell
```

From within the docker shell terminal run the following command for full tests:

```bash
./manage.py test dit_helpdesk --settings=config.settings.test
```

for testing a single app run e.g. the hierarchy app:

```bash
./manage.py test hierarchy.tests --settings=config.settings.test
```

for testing a single app's test module run e.g. the test_views in the the hierarchy app:

```bash
./manage.py test hierarchy.tests.test_views --settings=config.settings.test
```

and so on.

for coverage reports run any of the above commands via coverage e.g.

```bash
coverage run manage.py test dit_helpdesk --settings=config.settings.test
```

and then the reports can be generated:
```
coverage html
```
will write the reports to `test-reports/coverage_html` (configured in `.coveragerc`).

You will then be able to access the coverage report html from within your project folder's root
from your host machine in `test-reports/coverage_html`.

To write the reports to another folder, use:
```
coverage -d path/to/another_folder html
```

##### Updating modules

You will need to install pipenv stated above. Ensure Docker is running.
Update the version number in the Pipfile. There are 2 module lists; `dev-packages` and `packages`. The `dev-packages` are ONLY loaded in local
docker environments, while changes to the `packages` list are not always reflected in docker builds. Remember to test any updates locally and
on the dev environment by deploying the branch.

Get into the docker container by running the following:
```bash
docker-compose exec helpdesk /bin/bash
```

Generate updates to the Pipfile.lock file by running the following in the container:
```bash
pipenv lock
```
Do not manually update the Pipfile.lock file! Always auto generate it for the correct hashes!

## Management commands

### pull_api_update

```bash
./manage.py pull_api_update
```

This pulls the initial data from the trade tariff service API and stores the data in json files for future processing.

This will download the data for both the EU and the UK.

### prepare_import_data

```bash
./manage.py prepare_import_data
```

This takes the information downloaded from `pull_api_update` and transforms it by building the correct parent/child relationships in the data and removes any duplication.

This information is stored in json files.

#### Error: `Commodity found with no description`
This step may fail with the error `Commodity found with no description: [commodity code]` due to a missing description
in the data downloaded from the Trade Tariff  API by `pull_api_update`.
The team responsible for the Trade Tariff API should be notified of this so they can fix their data.

In the interim, the commodity code given can be used to find the correct description from public data sources.
This can then be added temporarily to the dict `dit_helpdesk.trade_tariff_service.HierarchyBuilder.PATCHED_DESCRIPTIONS`
with the commodity code as the key and the description as the value. That will allow `prepare_import_data`
to run to completion (or to the point at which another description is found to be missing).


### prepare_search_data

```bash
./manage.py prepare_search_data
```

This prepares the data from the `prepare_import_data` step by converting the json data into a csv format.

### scrape_section_hierarchy

```bash
./manage.py scrape_section_hierarchy
```

This creates the database instances of the nomenclature tree based on the data gathered from `prepare_import_data`.

This will generate the full nomenclature trees for the UK and the EU.

This doesn't activate the newly created tree but generates it ready for it to be activated in other steps.

### import_rules_of_origin

```bash
./manage.py import_rules_of_origin
```

Imports the rules of origin into the database. After the rules of origin are fully imported the rule text is post-processed for display purposes e.g. to display hyperlinks to the commodities a rule pertains to.

The rules of origin files are stored in an S3 bucket and this command will download these files and produce rules of origin objects tied to the currently active nomenclature tree.
For docker environments an instance of Minio is used in place of connecting to the S3 bucket. To set up the rules of origin in your local docker, you will need to follow these steps:

    1. Download & install CyberDuck

    2. Access Vault and from helpdesk/dev get the following secrets:
      ```
      ROO_S3_ACCESS_KEY
      ROO_S3_BUCKET_NAME
      ROO_SECRET_ACCESS_KEY
      ```

    3. Open CyberDuck and click the Plus symbol button on the main page to create a new connection

    4. In the popup window, fill in the following details:
	      - Select “Amazon S3” from the first dropdown box
	      - Type the ROO_S3_ACCESS_KEY into the Access Key Id box
	      - Type the ROO_SECRET_ACCESS_KEY into the Secret Access Key box
	      - Type the ROO_S3_BUCKET_NAME into the Path box

    5. With the connection created, double click on the connection to open the S3 bucket

    6. From this page copy the “rules_of_origin” folder to your local machine

    7. Move the rules_of_origin folder to the following path in the dit-helpdesk repo:
	    ```
      volumes/s3/import-rules-of-origin-bucket
      ```

    8. Access Vault and from helpdesk/docker_development get the following secrets:
	    ```
      S3_URL
	    ROO_S3_ACCESS_KEY
	    ROO_S3_BUCKET_NAME
	    ROO_SECRET_ACCESS_KEY
      ```

    9. Copy these secrets into your local .env file and restart the container

    10. Open the dit-helpdesk-helpdesk_1 container command line and shell in
      ```bash
      pipenv shell
      ```

    11. Run the command:
      ```bash
      ./manage.py import_rules_of_origin
      ```

### migrate_regulations

```bash
./manage.py migrate_regulations
```

This will link regulations that are attached to the previous nomenclature tree to the new tree which is to be activated (which will have been generated in other commands).

### export_scenarios

```bash
./manage.py export_scenarios -o YOUR_FILENAME_HERE.csv
```

Will create a csv file containing the details of all the countries trade agreement status currently in the DB.
Contains the following information:
"Country code" - 2 digit code used to represent country
"Country name" - Name of the country
"UK agreement status" - indicator to show if the country in question has a trade agreement with the UK
"EU agreement status"  - indicator to show if the country in question has a trade agreement with the European Union
"Scenario" - Code indicating what category of trade relationship this country has with the UK
"GOVUK FTA URL" - URL address of the trade agreement details page on the .gov website
"Trade Agreement Title" - The name of the trade agreement between this country and the UK (if applicable)
"Trade Agreement Type" - The type of trade agreement between this country and the UK (if applicable)

### generate_search_keywords

```bash
./manage.py generate_search_keywords -f search/data
```

This generates the search keywords for the nomenclature tree.

Outputs the keywords into a csv file.

### import_search_keywords

```bash
./manage.py import_search_keywords -f output/keywords_and_synonyms_merged.csv
```

Imports the search data from `generate_search_keywords` into the database models for the nomenclature tree.

### swap_rebuild_index

```bash
./manage.py swap_rebuild_index
```

Creates a new search index for the most recent nomenclature tree and swaps it out at the end.


[1]: https://nodejs.org/en/about/releases/
[2]: https://github.com/alphagov/govuk-frontend
[3]: https://github.com/alphagov/govuk-country-and-territory-autocomplete
[4]: https://github.com/alphagov/accessible-autocomplete
[5]: %60https://vault.ci.uktrade.io/ui/vault/secrets/dit%2Ftrade-helpdesk/list/helpdesk/%60
[6]: %60https://github.com/settings/tokens%60
[7]: %60https://vault.ci.uktrade.io%60
[8]: https://nodejs.org/en/about/releases/

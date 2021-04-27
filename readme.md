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

- Docker (if developing locally with docker)

### Install using Docker

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

#### pre-commit

Install pre-commit - a hook will execute Python and JS code formatters before
commit

```bash
pre-commit install
```

#### Install for development with Docker (recommended)

Make sure that Docker is installed and running.

```bash
docker-compose up -d
```

##### Initial setup run

This intial set up will take about an hour (depending upon machine and internet speed) to set up and fully import
all content, on subsequent runs it will on take a minute or so to be up and running for development.

NOTE: On first setup if you don't have the [Directory Forms API](https://github.com/uktrade/directory-forms-api/blob/develop/README.md) docker environment running you may receive the error:

    ERROR: Network directory-forms-api_outside-network declared as external, but could not be found. Please create the network manually using `docker network create directory-forms-api_outside-network` and try again.

You can either run the docker environment for Directory Forms API, which will create this network for you or create it manually using the command it gives.

Run the following command to activate a shell into the docker instance for the trade helpdesk app with the command.

```bash
docker-compose exec helpdesk /bin/bash
```

```bash
pipenv shell
./reload_data.sh
```

The site will be available at http://localhost:8000/choose-country/

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

create a hosts file entry for

# `127.0.0.1 forms.trade.great`

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

for testing a single app run i.e. the hierarchy app:

```bash
./manage.py test hierarchy.tests --settings=config.settings.test
```

for testing a single app's test module run i.e. the test_views in the the hierarchy app:

```bash
./manage.py test hierarchy.tests.test_views --settings=config.settings.test
```

and so on.

for coverage reports run any of the above commands via coverage e.g.

```bash
coverage run manage.py test dit_helpdesk --settings=config.settings.test
```

and then the reports can be generated
```
coverage -d reports html
```

you will then be able to access the coverage report html from within your project folder's root
from your host machine at /reports


[1]: https://nodejs.org/en/about/releases/
[2]: https://github.com/alphagov/govuk-frontend
[3]: https://github.com/alphagov/govuk-country-and-territory-autocomplete
[4]: https://github.com/alphagov/accessible-autocomplete
[5]: %60https://vault.ci.uktrade.io/ui/vault/secrets/dit%2Ftrade-helpdesk/list/helpdesk/%60
[6]: %60https://github.com/settings/tokens%60
[7]: %60https://vault.ci.uktrade.io%60
[8]: https://nodejs.org/en/about/releases/

# Exporting things to the UK (working title)

This service is used to help people find the correct Harmonised System (HS) code, duties, rules of origin etc for the products that they want to export to the UK.

## Requirements
 - Python 3
 - Node 10
 - Docker

 You can install and run this outside of Docker, but currently there is no documentation for this.

## Installation

First clone the repo, then using a terminal move inside of the folder:

```bash
cd dit-helpdesk
```

### Install using Docker

If you have Docker installed, you can run this service without needing to set up the database yourself, worrying about virtual environments - it's all within the Docker instance.

#### Frontend static assets

We need to install [GOV.UK Frontend](https://github.com/alphagov/govuk-frontend), [Accessible Autocomplete](https://github.com/alphagov/accessible-autocomplete), and other front end dependencies. This is all done by going to the project root folder, which contains `package.json`. Then run:

```bash
npm install
```

This will install all of the packages needed to build the front end static assets.

To build and move all of the static assets:

```bash
npm run build
```

To trigger a build when any Sass is changed, run:
```bash
npm run watch:styles
```

A list of all of the commands, including linting, can be found the the `package.json` file in the `scripts` object.

#### Installation

Make sure that Docker is installed and running. Then run:

```bash
docker-compose up
```

We need to populate the database with products. Shell into Docker by running:

```bash
docker exec -it dit-helpdesk_helpdesk_1 /bin/bash
```

You should now be in the root of the app. To populate the products in the database, we need to run a scrape. To get the products in Section I, run:

```bash
python dit_helpdesk/manage.py scrape_section_hierarchy 1
```

To get Section II, replace 1 with 2; Section III, use 3 - and so on. Recommend scraping at least one section. The scrape will take a while.

#### Running

Starting the server again is the same command as installing:

```bash
docker-compose up
```

The site will be available at http://localhost:8000

<!---
### Install locally
To run, we need to create a Python virtual environment and install any requirements.

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
pip install -r requirements.txt
```

Once that's done, we now have to configure the development set up. `cd` into `dit_helpdesk`, then run these three commands:

```bash
export PYTHONPATH=$(pwd)
```

```bash
export DJANGO_BASE_DIR=$(pwd)
```

```bash
export DJANGO_SETTINGS_MODULE=dit_helpdesk.settings.dev
```

To populate the products in the database, we need to run a scrape. To get the products in Section I, run:

```bash
python manage.py scrape_section_hierarchy 1
```

To get Section II, replace 1 with 2; Section III, use 3 - and so on. Recommend scraping at least one section. The scrape will take a while.

Now we need to [build the front end static assets](#frontend-build).

Once the scraping has finished and the front end assets are in place, start the server:

```bash
python manage.py runserver
```
-->

# Exporting things to the UK (working title)

This service is used to help people find the correct Harmonised System (HS) code, duties, rules of origin etc for the products that they want to export to the UK.

## Requirements
 - Python 3
 - Node [Active LTS](https://nodejs.org/en/about/releases/) version (Current Active version is v10)
 - Docker

 You can install and run this outside of Docker, but currently there is no documentation for this.

## Installation

First clone the repo, then using a terminal move inside of the folder:

```bash
cd dit-helpdesk
```

### Install using Docker

If you have Docker installed, you can run this service without needing to set up the database yourself, worrying about virtual environments - it's all within the Docker instance.

#### Frontend static asset installation

First we need to install [GOV.UK Frontend](https://github.com/alphagov/govuk-frontend) and
[GOV.UK country and territory autocomplete](https://github.com/alphagov/govuk-country-and-territory-autocomplete) (Which will also also install the required [Accessible Autocomplete](https://github.com/alphagov/accessible-autocomplete) dependency), and other front end dependencies.

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

#### Installation

Make sure that Docker is installed and running. Open `start.sh` and comment back in the pip installation

```bash
pip install -r requirements.txt
```

Then run:

```bash
docker-compose build
```

Once the build has completed, comment out the pip installation in `start.sh` - this isn't essential, but it will save you time when booting up the docker instance.

Now run:

```bash
docker-compose up
```

We need to populate the database with products. Shell into Docker by running:

```bash
docker exec -it dit-helpdesk_helpdesk_1 /bin/bash
```

You should now be in the root of the app. To populate the products in the database, we need to run a scrape. To get the products in Section I, run:

```bash
python dit_helpdesk/manage.py scrape_section_hierarchy_v2
```

To get Section II, replace 1 with 2; Section III, use 3 - and so on. Recommend scraping at least one section. The scrape will take a while.

#### Update Environment variables in case you get Sentry exceptions (Optional)
If `docker-compose.env` file does not exists, create it by copying `docker-compose.conf.env`

You will need to access [Helpdesk Vault](`https://vault.ci.uktrade.io/ui/vault/secrets/dit%2Ftrade-helpdesk/list/helpdesk/`) to get the required enviroment variable secrets to use them in the file. To do so you will to generate a github personal access token. This is needed to log into vault. Go here: [Vault](`https://github.com/settings/tokens`) click `Generate new token` and make sure it has these scopes: `read:org`, `read:user`. Once you've done that, head over to [Vault](`https://vault.ci.uktrade.io`) and login with the token. You'll need to select github as your login option.

### Running

Starting the server again is the same command as installing:

```bash
docker-compose up
```

The site will be available at http://localhost:8000/choose-country/.

To trigger a build when any Sass is changed, run:
```bash
npm run watch:styles
```

### Running, then shelling in

If you want to be able to run commands in bash within the docker instance, we need to change the start script `start.sh` slightly.

Comment out the line that starts the app, and comment back in the sleep command. So it should read:
```shell
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

## Country synonyms

The list of all countries that need to be listed is in `assets/countries/countries-data.json`. If the countries and/or synonyms need to be updated, change the `countries-data.json` to add countries; and change `add-synonyms.js` file to add synonyms. Then run `npm run update-countries`. You should see the updated files in `dit_helpdesk/static_collected/js/`.


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


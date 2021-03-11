# Generated by Django 2.2.13 on 2021-03-08 17:19

import csv
import logging
import os

from django.db import migrations

from . import DATA_DIR


def true_or_false(val):
    return val == "Y" or val == "TRUE" or val == "True"


def update_trade_scenarios(apps, schema_editor):
    Country = apps.get_model("countries", "Country")

    csv_file_path = os.path.join(DATA_DIR, "trade-scenarios-2021-03-08.csv")
    with open(csv_file_path) as csv_data:
        reader = csv.DictReader(csv_data)

        updated_country_codes = []
        for row in reader:
            country_code = row["Country code"]
            try:
                country = Country.objects.get(country_code=country_code)
            except Country.DoesNotExist:
                logging.warning("Country %s does not exist", country_code)
                continue

            country.content_url = row["GOVUK FTA URL"]
            country.scenario = row["Scenario"]
            country.has_uk_trade_agreement = true_or_false(row["UK agreement status"])
            country.has_eu_trade_agreement = true_or_false(row["EU agreement status"])
            country.save()

            updated_country_codes.append(country_code)

        not_updated_countries = Country.objects.exclude(country_code__in=updated_country_codes).values_list("country_code", flat=True)
        not_updated_countries = list(not_updated_countries)
        if not_updated_countries:
            logging.warning("Did not update %s", not_updated_countries)


class Migration(migrations.Migration):

    dependencies = [
        ('countries', '0013_update_trade_scenarios_2021_01_11'),
    ]

    operations = [
        migrations.RunPython(
            update_trade_scenarios,
            migrations.RunPython.noop,
        )
    ]
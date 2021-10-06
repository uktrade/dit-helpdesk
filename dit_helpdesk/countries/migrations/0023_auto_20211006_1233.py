# Generated by Django 2.2.24 on 2021-10-06 11:33

from django.db import migrations
import logging


def fix_countries_trade_names(apps, schema_editor):
    # Fixing the two data errors in the last migration:
    # Kosovo,"UK-Kosovo?partnership, trade and cooperation?agreement",
    # North Macedonia,"UK-North Macedonia Partnership, Trade and?Cooperation?agreement"
    # Need to remove the "?" and replace with a regular space.
    Country = apps.get_model("countries", "Country")

    country_fix_list = ["Kosovo", "North Macedonia"]

    for country_name in country_fix_list:
        try:
            country = Country.objects.get(name=country_name)
            country.trade_agreement_title = country.trade_agreement_title.replace(
                "?", " "
            )
            country.save()
        except Exception:
            logging.warning("Did not update trade agreement title for " + country_name)


def verify_change(apps, schema_editor):
    Country = apps.get_model("countries", "Country")
    countries_table = Country.objects.all()

    for country in countries_table:
        logging.info(
            "Name: "
            + country.name
            + " Scenario: "
            + country.scenario
            + " URL: "
            + country.content_url
        )
        if country.scenario is None:
            raise ValueError(
                "Scenario data has not been copied for " + country.country_name
            )
        if country.content_url is None:
            raise ValueError("URL data has not been copied for " + country.country_name)


class Migration(migrations.Migration):

    dependencies = [
        ("countries", "0022_auto_20210924_1604"),
    ]

    # Steps:
    # 1. Rename old scenario & URL columns to move them out of the way
    # 2. Rename new scenario & URL columns to make them "current"
    # 3. Verify the rename has not wiped the column data
    # 4. Delete the "old_" columns for good (cannot be reversed once done)
    # 5. Run trade agreement name fix

    operations = [
        migrations.RenameField(
            model_name="country",
            old_name="content_url",
            new_name="old_content_url",
        ),
        migrations.RenameField(
            model_name="country",
            old_name="scenario",
            new_name="old_scenario",
        ),
        migrations.RenameField(
            model_name="country",
            old_name="new_trade_agreement_url",
            new_name="content_url",
        ),
        migrations.RenameField(
            model_name="country",
            old_name="new_scenario",
            new_name="scenario",
        ),
        migrations.RunPython(verify_change, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="country",
            name="old_content_url",
        ),
        migrations.RemoveField(
            model_name="country",
            name="old_scenario",
        ),
        migrations.RunPython(fix_countries_trade_names, migrations.RunPython.noop),
    ]

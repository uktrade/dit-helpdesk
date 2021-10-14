# Generated by Django 2.2.24 on 2021-10-08 15:02

import os, csv, logging
from . import DATA_DIR
from countries.models import Country
from django.db import migrations, models


def fix_countries_trade_names(apps, schema_editor):
    # Fixing the two data errors in the last migration:
    # Kosovo,"UK-Kosovo?partnership, trade and cooperation?agreement",
    # North Macedonia,"UK-North Macedonia Partnership, Trade and?Cooperation?agreement"
    # Need to remove the "?" and replace with a regular space.
    Country = apps.get_model("countries", "Country")

    country_fix_list = ["Kosovo", "North Macedonia"]
    for country_name in country_fix_list:
        country = Country.objects.get(name=country_name)
        country.trade_agreement_title = country.trade_agreement_title.replace("?", " ")
        country.save()


class Migration(migrations.Migration):

    dependencies = [
        ("countries", "0024_auto_20211007_1049"),
    ]

    # 1. Make scenario column nullable, so if reverting column delete we wont error
    # 2. Rename scenario and content_url columns to make way for new columns to take their place
    # 3. Backup old scenarios, content_urls and uk trade agreement status before deleting in next pr
    # 4. Apply data fix for Kosovo and N.Macedonia trade agreement names

    operations = [
        migrations.RenameField(
            model_name="country",
            old_name="content_url",
            new_name="old_content_url",
        ),
        migrations.AlterField(
            model_name="country",
            name="scenario",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.RenameField(
            model_name="country",
            old_name="scenario",
            new_name="old_scenario",
        ),
        migrations.RunPython(fix_countries_trade_names, migrations.RunPython.noop),
    ]

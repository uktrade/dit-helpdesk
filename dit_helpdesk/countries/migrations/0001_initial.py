# Generated by Django 2.1.5 on 2019-02-13 20:30

import csv
import os

from django.db import migrations, models

from . import DATA_DIR


def init_countries(apps, schema_editor):
    Country = apps.get_model("countries", "Country")

    countries_file_path = os.path.join(DATA_DIR, "initial-countries.csv")
    with open(countries_file_path) as countries_file:
        reader = csv.DictReader(countries_file)

        for row in reader:
            Country.objects.create(country_code=row["country_code"], name=row["name"])


def remove_all_countries(apps, schema_editor):
    Country = apps.get_model("countries", "Country")

    Country.objects.all().delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("country_code", models.CharField(max_length=2)),
                ("name", models.CharField(max_length=250)),
            ],
        ),
        migrations.RunPython(init_countries, remove_all_countries),
    ]

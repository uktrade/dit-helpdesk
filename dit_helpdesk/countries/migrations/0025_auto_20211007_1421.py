# Generated by Django 2.2.24 on 2021-10-07 13:21

import os, csv
from countries.models import Country
from django.db import migrations, models
from . import DATA_DIR


def backup_old_scenarios(apps, schema_editor):
    fieldnames = ["country_code", "scenario", "content_url"]

    csv_file_path = os.path.join(DATA_DIR, "migration_0025_backup.csv")

    with open(csv_file_path, "w") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        csv_writer.writeheader()

        for country in Country.objects.order_by("country_code"):
            csv_writer.writerow(
                {
                    "country_code": country.country_code,
                    "scenario": country.scenario,
                    "content_url": country.content_url,
                }
            )


class Migration(migrations.Migration):

    dependencies = [
        ("countries", "0024_auto_20211007_1049"),
    ]

    # 1. Save column contents to CSV file for backup
    # 2. Make scenario column nullable in case of rollback
    # 3. Rename fields to make way for new versions to be renamed

    operations = [
        migrations.RunPython(backup_old_scenarios, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="country",
            name="scenario",
            field=models.CharField(max_length=255, null=True),
        ),
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
    ]

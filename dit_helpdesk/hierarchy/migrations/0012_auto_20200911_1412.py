# Generated by Django 2.2.13 on 2020-09-11 13:12
import django_migration_linter as linter

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("hierarchy", "0011_auto_20200910_1653")]

    operations = [
        linter.IgnoreMigration(),
        migrations.AlterField(
            model_name="nomenclaturetree",
            name="end_date",
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name="nomenclaturetree",
            name="start_date",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

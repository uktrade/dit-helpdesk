# Generated by Django 2.2.13 on 2020-10-06 12:18
import django_migration_linter as linter

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("hierarchy", "0014_remove_tts_json")]

    operations = [
        linter.IgnoreMigration(),
        migrations.RemoveField(model_name="heading", name="last_updated"),
        migrations.RemoveField(model_name="subheading", name="last_updated"),
    ]

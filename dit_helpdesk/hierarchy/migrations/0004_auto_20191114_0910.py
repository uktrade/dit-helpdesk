# Generated by Django 2.2.6 on 2019-11-14 09:10
import django_migration_linter as linter

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("hierarchy", "0003_subheading_tts_json")]

    operations = [
        linter.IgnoreMigration(),
        migrations.RenameField(
            model_name="subheading", old_name="tts_is_leaf", new_name="leaf"
        )
    ]

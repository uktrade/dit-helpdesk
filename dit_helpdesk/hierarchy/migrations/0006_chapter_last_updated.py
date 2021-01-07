# Generated by Django 2.2.6 on 2019-12-03 19:49
import django_migration_linter as linter

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("hierarchy", "0005_chapter_tts_json")]

    operations = [
        linter.IgnoreMigration(),
        migrations.AddField(
            model_name="chapter",
            name="last_updated",
            field=models.DateTimeField(auto_now=True),
        )
    ]

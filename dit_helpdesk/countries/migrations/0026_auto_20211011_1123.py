# Generated by Django 2.2.24 on 2021-10-11 10:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("countries", "0025_auto_20211008_1602"),
    ]

    operations = [
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
        migrations.RemoveField(
            model_name="country",
            name="old_content_url",
        ),
        migrations.RemoveField(
            model_name="country",
            name="old_scenario",
        ),
        migrations.RemoveField(
            model_name="country",
            name="has_uk_trade_agreement",
        ),
    ]

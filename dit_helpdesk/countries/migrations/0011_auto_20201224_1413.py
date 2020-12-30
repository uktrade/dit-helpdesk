# Generated by Django 2.2.13 on 2020-12-24 14:13

from django.db import migrations


def update_country_name(apps, schema_editor):
    Country = apps.get_model("countries", "Country")

    try:
        country = Country.objects.get(country_code="PS")
    except Country.DoesNotExist:
        return

    country.name = "The Occupied Palestinian Territories"
    country.save()


class Migration(migrations.Migration):

    dependencies = [
        ('countries', '0010_update_trade_scenarios_2020_12_24'),
    ]

    operations = [
        migrations.RunPython(
            update_country_name,
            migrations.RunPython.noop,
        )
    ]
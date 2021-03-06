# Generated by Django 2.2.13 on 2020-12-23 14:59

from django.db import migrations


def forward_set_is_eu(apps, schema_editor):
    Country = apps.get_model("countries", "Country")

    country_codes = [
        "HR",
        "CY",
        "CZ",
        "EE",
        "FI",
        "FR",
        "DE",
        "HU",
        "IE",
        "LV",
        "LT",
        "MT",
        "NL",
        "PL",
        "RO",
        "SK",
        "SI",
        "ES",
        "AT",
        "BE",
        "BG",
        "DK",
        "GR",
        "LU",
        "PT",
        "SE",
        "IT",
    ]
    Country.objects.update(is_eu=False)

    Country.objects.filter(country_code__in=country_codes).update(is_eu=True)


def backwards_set_is_eu(apps, schema_editor):
    Country = apps.get_model("countries", "Country")

    Country.objects.all().update(is_eu=False)


class Migration(migrations.Migration):

    dependencies = [("countries", "0008_country_is_eu")]

    operations = [migrations.RunPython(forward_set_is_eu, backwards_set_is_eu)]

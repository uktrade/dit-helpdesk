# Generated by Django 2.2.13 on 2020-12-14 14:38

from django.db import migrations


def forward_update_trade_agreements(apps, schema_editor):
    Country = apps.get_model("countries", "Country")

    # (SCENARIO, HAS_UK, HAS_EU)
    mapping = [
        ("ANDEAN-COUNTRIES", True, True),
        ("AUSTRALIA", False, False),
        ("EU-AGR-SIGNED-LINK", True, True),
        ("EU-AGR-SIGNED-NO-LINK", True, True),
        ("EU-MEMBER", False, True),
        ("EU-NOAGR-FOR-EXIT", False, True),
        ("ICELAND-NORWAY", True, True),
        ("JP", True, True),
        ("NEW-ZEALAND", False, False),
        ("US", False, False),
        ("WTO", False, False),
    ]

    for scenario, has_uk_trade_agreement, has_eu_trade_agreement in mapping:
        Country.objects.filter(
            scenario=scenario,
        ).update(
            has_uk_trade_agreement=has_uk_trade_agreement,
            has_eu_trade_agreement=has_eu_trade_agreement,
        )


def backwards_update_trade_agreements(apps, schema_editor):
    Country = apps.get_model("countries", "Country")
    Country.objects.update(
        has_uk_trade_agreement=False,
        has_eu_trade_agreement=False,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('countries', '0006_auto_20201214_1437'),
    ]

    operations = [
        migrations.RunPython(forward_update_trade_agreements, backwards_update_trade_agreements)
    ]
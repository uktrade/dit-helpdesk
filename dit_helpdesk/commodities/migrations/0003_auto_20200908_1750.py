# Generated by Django 2.2.13 on 2020-09-08 16:50
import datetime as dt

from django.db import migrations


def fill_nomenclature_tree(apps, schema_editor):
    Commodity = apps.get_model('commodities', 'Commodity')
    NomenclatureTree = apps.get_model('hierarchy', 'NomenclatureTree')

    tree = NomenclatureTree.objects.first()
    if not tree:
        tree = NomenclatureTree.objects.create(
            region='EU',
            start_date=dt.datetime.today(),
            end_date=None
        )

    Commodity.objects.all().update(nomenclature_tree=tree)


def unfill_nomenclature_tree(apps, schema_editor):
    Commodity = apps.get_model('commodities', 'Commodity')

    Commodity.objects.all().update(nomenclature_tree=None)


class Migration(migrations.Migration):

    dependencies = [
        ('commodities', '0002_commodity_nomenclature_tree'),
    ]

    operations = [
        migrations.RunPython(fill_nomenclature_tree, unfill_nomenclature_tree)
    ]
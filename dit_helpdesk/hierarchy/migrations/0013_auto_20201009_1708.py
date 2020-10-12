# Generated by Django 2.2.13 on 2020-10-09 16:08
from django.db import migrations


def swap_nomenclature_trees(apps, schema_editor):
    NomenclatureTree = apps.get_model('hierarchy', 'NomenclatureTree')

    uk_trees = NomenclatureTree.objects.filter(region='UK')
    eu_trees = NomenclatureTree.objects.filter(region='EU')

    uk_trees.update(region='EU')
    eu_trees.update(region='UK')


class Migration(migrations.Migration):

    dependencies = [
        ('hierarchy', '0012_auto_20200911_1412'),
    ]

    operations = [
        migrations.RunPython(swap_nomenclature_trees, swap_nomenclature_trees)
    ]

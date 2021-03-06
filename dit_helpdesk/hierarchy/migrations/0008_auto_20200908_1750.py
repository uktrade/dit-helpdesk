# Generated by Django 2.2.13 on 2020-09-08 16:50

from django.db import migrations

import datetime as dt

from django.db import migrations


def fill_nomenclature_tree(apps, schema_editor):
    Section = apps.get_model("hierarchy", "Section")
    Chapter = apps.get_model("hierarchy", "Chapter")
    Heading = apps.get_model("hierarchy", "Heading")
    SubHeading = apps.get_model("hierarchy", "SubHeading")
    NomenclatureTree = apps.get_model("hierarchy", "NomenclatureTree")

    tree = NomenclatureTree.objects.first()
    if not tree:
        tree = NomenclatureTree.objects.create(
            region="EU", start_date=dt.datetime.today(), end_date=None
        )

    Section.objects.all().update(nomenclature_tree=tree)
    Chapter.objects.all().update(nomenclature_tree=tree)
    Heading.objects.all().update(nomenclature_tree=tree)
    SubHeading.objects.all().update(nomenclature_tree=tree)


def unfill_nomenclature_tree(apps, schema_editor):
    Section = apps.get_model("hierarchy", "Section")
    Chapter = apps.get_model("hierarchy", "Chapter")
    Heading = apps.get_model("hierarchy", "Heading")
    SubHeading = apps.get_model("hierarchy", "SubHeading")

    Section.objects.all().update(nomenclature_tree=None)
    Chapter.objects.all().update(nomenclature_tree=None)
    Heading.objects.all().update(nomenclature_tree=None)
    SubHeading.objects.all().update(nomenclature_tree=None)


class Migration(migrations.Migration):

    dependencies = [("hierarchy", "0007_auto_20200908_1750")]

    operations = [
        migrations.RunPython(fill_nomenclature_tree, unfill_nomenclature_tree)
    ]

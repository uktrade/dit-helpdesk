# Generated by Django 2.2.13 on 2020-09-10 15:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hierarchy', '0010_auto_20200910_1650'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='subheading',
            unique_together={('commodity_code', 'description', 'nomenclature_tree')},
        ),
    ]
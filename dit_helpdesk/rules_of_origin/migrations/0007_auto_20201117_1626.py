# Generated by Django 2.2.13 on 2020-11-17 16:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules_of_origin', '0006_auto_20201117_1233'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rule',
            old_name='rule_id',
            new_name='description',
        ),
    ]

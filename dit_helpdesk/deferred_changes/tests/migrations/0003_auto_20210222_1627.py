# Generated by Django 2.2.13 on 2021-02-22 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0002_auto_20210222_1558'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TestModel',
            new_name='ChildModel',
        ),
    ]

# Generated by Django 2.2.13 on 2020-09-23 10:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commodities', '0006_auto_20200910_1650'),
        ('hierarchy', '0012_auto_20200911_1412'),
        ('regulations', '0002_auto_20200909_1646'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Regulation',
            new_name='RegulationGroup',
        ),
        migrations.AlterModelOptions(
            name='regulationgroup',
            options={},
        ),
        migrations.RenameField(
            model_name='document',
            old_name='regulations',
            new_name='regulation_groups',
        ),
    ]
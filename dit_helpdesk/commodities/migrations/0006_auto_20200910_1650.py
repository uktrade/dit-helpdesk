# Generated by Django 2.2.13 on 2020-09-10 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commodities', '0005_auto_20200910_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commodity',
            name='commodity_code',
            field=models.CharField(max_length=10),
        ),
    ]

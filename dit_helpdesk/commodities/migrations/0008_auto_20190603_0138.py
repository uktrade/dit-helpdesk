# Generated by Django 2.1.5 on 2019-06-03 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commodities', '0007_auto_20190529_0924'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commodity',
            name='ranking',
            field=models.SmallIntegerField(null=True),
        ),
    ]

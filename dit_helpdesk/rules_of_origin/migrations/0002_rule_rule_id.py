# Generated by Django 2.1.5 on 2019-04-03 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rules_of_origin', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rule',
            name='rule_id',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]

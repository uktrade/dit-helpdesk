# Generated by Django 2.2.13 on 2020-09-18 08:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("rules_of_origin", "0002_auto_20200917_1201")]

    operations = [
        migrations.AlterModelOptions(name="ruleitem", options={"ordering": ["order"]})
    ]

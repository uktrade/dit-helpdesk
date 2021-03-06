# Generated by Django 2.2.13 on 2020-12-09 21:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("rules_of_origin", "0012_auto_20201208_1817")]

    operations = [
        migrations.AlterField(
            model_name="oldrulesdocumentfootnote",
            name="old_rules_document",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="old_footnotes",
                to="rules_of_origin.OldRulesDocument",
            ),
        )
    ]

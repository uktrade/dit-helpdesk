# Generated by Django 3.2.10 on 2021-12-30 15:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rules_of_origin", "0021_auto_20211206_1427"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="rule",
            name="alt_rule_text_processed",
        ),
        migrations.RemoveField(
            model_name="rule",
            name="description_processed",
        ),
        migrations.RemoveField(
            model_name="rule",
            name="rule_text_processed",
        ),
        migrations.RemoveField(
            model_name="subrule",
            name="alt_rule_text_processed",
        ),
        migrations.RemoveField(
            model_name="subrule",
            name="description_processed",
        ),
        migrations.RemoveField(
            model_name="subrule",
            name="rule_text_processed",
        ),
    ]
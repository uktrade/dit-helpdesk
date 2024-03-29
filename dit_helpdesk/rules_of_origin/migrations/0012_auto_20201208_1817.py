# Generated by Django 2.2.13 on 2020-12-08 18:17
import django_migration_linter as linter

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("countries", "0005_auto_20201119_1450"),
        ("hierarchy", "0017_nomenclaturetree_source"),
        ("rules_of_origin", "0011_auto_20201208_1729"),
    ]

    operations = [
        linter.IgnoreMigration(),
        migrations.RenameModel(old_name="Old_Rule", new_name="OldRule"),
        migrations.RenameModel(old_name="Old_RuleItem", new_name="OldRuleItem"),
        migrations.RenameModel(
            old_name="Old_RulesDocument", new_name="OldRulesDocument"
        ),
        migrations.RenameModel(
            old_name="Old_RulesDocumentFootnote", new_name="OldRulesDocumentFootnote"
        ),
        migrations.RenameModel(old_name="Old_RulesGroup", new_name="OldRulesGroup"),
        migrations.RenameModel(
            old_name="Old_RulesGroupMember", new_name="OldRulesGroupMember"
        ),
    ]

# Generated by Django 2.2.13 on 2020-11-17 12:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hierarchy', '0016_remove_chapter_last_updated'),
        ('countries', '0004_auto_20201021_1041'),
        ('rules_of_origin', '0004_rulesdocument_start_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('description', models.TextField(blank=True, null=True)),
                ('rule_text', models.TextField(blank=True, null=True)),
                ('alt_rule_text', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='rulesgroupmember',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='rulesgroupmember',
            name='country',
        ),
        migrations.RemoveField(
            model_name='rulesgroupmember',
            name='rules_group',
        ),
        migrations.AlterModelOptions(
            name='rulesdocumentfootnote',
            options={'ordering': ['number'], 'verbose_name_plural': 'rules document footnotes'},
        ),
        migrations.AddField(
            model_name='rule',
            name='alt_rule_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rule',
            name='headings',
            field=models.ManyToManyField(blank=True, null=True, related_name='rules_of_origin', to='hierarchy.Heading'),
        ),
        migrations.AddField(
            model_name='rule',
            name='rule_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rulesdocument',
            name='countries',
            field=models.ManyToManyField(related_name='rules_documents', to='countries.Country'),
        ),
        migrations.AddField(
            model_name='rulesdocument',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='rulesdocumentfootnote',
            name='identifier',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='rulesdocumentfootnote',
            name='link_html',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='rulesdocument',
            unique_together={('source_url',)},
        ),
        migrations.DeleteModel(
            name='RuleItem',
        ),
        migrations.DeleteModel(
            name='RulesGroupMember',
        ),
        migrations.AddField(
            model_name='subrule',
            name='rule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rules_of_origin.Rule'),
        ),
        migrations.RemoveField(
            model_name='rulesdocument',
            name='rules_group',
        ),
        migrations.DeleteModel(
            name='RulesGroup',
        ),
    ]
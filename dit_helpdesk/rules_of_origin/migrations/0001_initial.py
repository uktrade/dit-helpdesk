# Generated by Django 2.2.2 on 2019-08-20 06:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hierarchy', '0001_initial'),
        ('countries', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RulesDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('source_url', models.URLField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'rules of origin documents',
            },
        ),
        migrations.CreateModel(
            name='RulesGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name_plural': 'rules of origin',
            },
        ),
        migrations.CreateModel(
            name='RulesDocumentFootnote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField()),
                ('link_html', models.TextField()),
                ('note', models.TextField()),
                ('rules_document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='footnotes', to='rules_of_origin.RulesDocument')),
            ],
            options={
                'verbose_name_plural': 'rules document footnotes',
            },
        ),
        migrations.AddField(
            model_name='rulesdocument',
            name='rules_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rules_of_origin.RulesGroup'),
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_id', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('working_or_processing_one', models.TextField(blank=True, null=True)),
                ('working_or_processing_two', models.TextField(blank=True, null=True)),
                ('is_exclusion', models.BooleanField(default=False)),
                ('chapter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rules_of_origin', to='hierarchy.Chapter')),
                ('rules_document', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='rules_of_origin.RulesDocument')),
            ],
            options={
                'verbose_name_plural': 'rules of origin',
            },
        ),
        migrations.CreateModel(
            name='RulesGroupMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('finish_date', models.DateField(blank=True, null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='countries.Country')),
                ('rules_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rules_of_origin.RulesGroup')),
            ],
            options={
                'verbose_name_plural': 'rules of origin group members',
                'unique_together': {('country', 'rules_group', 'start_date')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='rulesdocument',
            unique_together={('rules_group', 'source_url')},
        ),
    ]

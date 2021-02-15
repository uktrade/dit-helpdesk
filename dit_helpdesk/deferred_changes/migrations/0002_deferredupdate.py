# Generated by Django 2.2.13 on 2021-02-15 11:34

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('deferred_changes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeferredUpdate',
            fields=[
                ('deferredchange_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='deferred_changes.DeferredChange')),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('form_class', models.CharField(max_length=255)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('deferred_changes.deferredchange',),
        ),
    ]

# Generated by Django 2.1.5 on 2019-01-21 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requirements_documents', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abstractcommodity',
            name='tts_is_leaf',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='commodity',
            name='tts_is_leaf',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]

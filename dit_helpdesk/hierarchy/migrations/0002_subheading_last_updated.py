# Generated by Django 2.2.5 on 2019-10-07 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hierarchy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subheading',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

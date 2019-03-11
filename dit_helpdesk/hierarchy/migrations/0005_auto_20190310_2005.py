# Generated by Django 2.1.5 on 2019-03-10 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hierarchy', '0004_auto_20190310_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='position',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='section',
            name='roman_numeral',
            field=models.CharField(max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='section',
            name='title',
            field=models.TextField(blank=True, null=True),
        ),
    ]

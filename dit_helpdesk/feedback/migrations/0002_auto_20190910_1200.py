# Generated by Django 2.2.2 on 2019-09-10 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("feedback", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="feedback", name="email", field=models.EmailField(max_length=254)
        ),
        migrations.AlterField(
            model_name="feedback", name="name", field=models.CharField(max_length=255)
        ),
    ]

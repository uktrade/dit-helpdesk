# Generated by Django 2.2.2 on 2019-08-20 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('commodities', '0001_initial'),
        ('hierarchy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Regulation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('commodities', models.ManyToManyField(to='commodities.Commodity')),
                ('headings', models.ManyToManyField(to='hierarchy.Heading')),
                ('subheadings', models.ManyToManyField(to='hierarchy.SubHeading')),
            ],
            options={
                'verbose_name_plural': 'regulations',
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('type', models.CharField(max_length=255)),
                ('celex', models.CharField(max_length=20)),
                ('url', models.URLField()),
                ('regulations', models.ManyToManyField(to='regulations.Regulation')),
            ],
            options={
                'verbose_name': 'regulation document',
                'verbose_name_plural': 'regulations documents',
            },
        ),
    ]

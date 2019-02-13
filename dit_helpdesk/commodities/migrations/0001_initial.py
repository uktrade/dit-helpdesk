# Generated by Django 2.1.5 on 2019-02-13 20:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hierarchy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commodity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commodity_code', models.CharField(max_length=10, unique=True)),
                ('goods_nomenclature_sid', models.CharField(max_length=10)),
                ('tts_json', models.TextField(blank=True, null=True)),
                ('tts_heading_json', models.TextField(blank=True, null=True)),
                ('tts_number_indents', models.IntegerField(blank=True, null=True)),
                ('tts_is_leaf', models.BooleanField(blank=True, null=True)),
                ('tts_section_position', models.IntegerField(blank=True, null=True)),
                ('heading', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_concrete', to='hierarchy.Heading')),
                ('parent_subheading', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_concrete', to='hierarchy.SubHeading')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='commodity',
            unique_together={('commodity_code', 'goods_nomenclature_sid')},
        ),
    ]

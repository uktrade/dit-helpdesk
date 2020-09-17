# Generated by Django 2.2.13 on 2020-09-08 19:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hierarchy', '0008_auto_20200908_1750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='nomenclature_tree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hierarchy.NomenclatureTree'),
        ),
        migrations.AlterField(
            model_name='heading',
            name='nomenclature_tree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hierarchy.NomenclatureTree'),
        ),
        migrations.AlterField(
            model_name='section',
            name='nomenclature_tree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hierarchy.NomenclatureTree'),
        ),
        migrations.AlterField(
            model_name='subheading',
            name='nomenclature_tree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hierarchy.NomenclatureTree'),
        ),
    ]
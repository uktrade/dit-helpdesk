# Generated by Django 2.2.13 on 2020-10-07 17:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regulations', '0006_auto_20201007_1833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regulation',
            name='nomenclature_tree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hierarchy.NomenclatureTree'),
        ),
        migrations.AlterField(
            model_name='regulationgroup',
            name='nomenclature_tree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hierarchy.NomenclatureTree'),
        ),
    ]

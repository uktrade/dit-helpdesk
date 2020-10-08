# Generated by Django 2.2.13 on 2020-10-07 17:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hierarchy', '0012_auto_20200911_1412'),
        ('regulations', '0004_auto_20200923_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='regulation',
            name='nomenclature_tree',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='hierarchy.NomenclatureTree'),
        ),
        migrations.AddField(
            model_name='regulationgroup',
            name='nomenclature_tree',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='hierarchy.NomenclatureTree'),
        ),
    ]

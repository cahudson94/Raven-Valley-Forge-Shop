# Generated by Django 2.0 on 2018-09-24 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0026_auto_20180917_2300'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='active_discount',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='account',
            name='cell_number',
            field=models.CharField(blank=True, max_length=14),
        ),
    ]

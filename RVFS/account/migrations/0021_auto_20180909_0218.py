# Generated by Django 2.0 on 2018-09-09 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0020_auto_20180828_2242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='about',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='account',
            name='group',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
    ]
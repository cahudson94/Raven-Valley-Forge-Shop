# Generated by Django 2.0 on 2018-08-28 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0019_auto_20180224_1938'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='about',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='account',
            name='group',
            field=models.CharField(default='', max_length=30),
        ),
    ]

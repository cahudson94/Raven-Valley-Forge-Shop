# Generated by Django 2.0 on 2018-09-27 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0023_auto_20180927_1018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='blurb',
        ),
    ]

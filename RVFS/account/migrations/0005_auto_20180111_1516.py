# Generated by Django 2.0 on 2018-01-11 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20180111_1435'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shippinginfo',
            old_name='residents',
            new_name='resident',
        ),
    ]

# Generated by Django 2.0 on 2018-01-18 21:47

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_auto_20180118_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='diamiter',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('1/8', '1/8'), ('1/4', '1/4'), ('3/8', '3/8'), ('1/2', '1/2'), ('5/8', '5/8')], default='', max_length=150),
        ),
        migrations.AlterField(
            model_name='product',
            name='length',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('4', 4), ('5', 5), ('6', 6), ('7', 7), ('8', 8), ('9', 9), ('10', 10), ('11', 11), ('12', 12), ('13', 13), ('14', 14), ('15', 15), ('16', 16)], default='', max_length=150),
        ),
    ]
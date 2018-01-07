# Generated by Django 2.0 on 2018-01-07 03:00

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20180107_0109'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='product',
            name='diamiter',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('1/8', '1/8'), ('1/4', '1/4'), ('3/8', '3/8'), ('1/2', '1/2'), ('5/8', '5/8')], default='', max_length=150),
        ),
        migrations.AddField(
            model_name='product',
            name='extra_options',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='product',
            name='length',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('4', 4), ('5', 5), ('6', 6), ('7', 7), ('8', 8), ('9', 9), ('10', 10), ('11', 11), ('12', 12), ('13', 13), ('14', 14), ('15', 15), ('16', 16)], default='', max_length=150),
        ),
        migrations.AddField(
            model_name='product',
            name='shipping_info',
            field=models.TextField(blank=True, max_length=180),
        ),
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

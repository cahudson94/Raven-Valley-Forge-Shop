# Generated by Django 2.0 on 2018-01-07 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='decription',
            field=models.TextField(default=''),
        ),
    ]

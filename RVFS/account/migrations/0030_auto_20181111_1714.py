# Generated by Django 2.0 on 2018-11-11 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0029_account_active_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippinginfo',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Location Name'),
        ),
    ]

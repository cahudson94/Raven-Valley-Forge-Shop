# Generated by Django 2.0 on 2018-01-14 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='pic',
            field=models.ImageField(blank=True, upload_to='profile_pics'),
        ),
    ]

# Generated by Django 2.0 on 2018-09-27 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0024_remove_service_blurb'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='blurb',
            field=models.TextField(blank=True, default=''),
        ),
    ]
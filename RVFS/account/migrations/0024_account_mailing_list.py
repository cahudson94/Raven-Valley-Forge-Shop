# Generated by Django 2.0 on 2018-09-12 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0023_account_newsletter'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='mailing_list',
            field=models.TextField(blank=True, default=''),
        ),
    ]
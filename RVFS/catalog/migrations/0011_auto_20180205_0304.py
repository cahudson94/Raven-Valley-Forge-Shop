# Generated by Django 2.0 on 2018-02-05 03:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0010_userserviceimages'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserServiceImages',
            new_name='UserServiceImage',
        ),
    ]

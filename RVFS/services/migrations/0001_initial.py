# Generated by Django 2.0 on 2018-01-06 06:31

from django.db import migrations, models
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', sorl.thumbnail.fields.ImageField(upload_to='images')),
                ('published', models.CharField(choices=[('PB', 'public'), ('PV', 'private')], default='PV', max_length=2)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_published', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('decription', models.TextField()),
            ],
        ),
    ]
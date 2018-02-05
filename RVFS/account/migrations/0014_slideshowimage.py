# Generated by Django 2.0 on 2018-02-05 05:24

from django.db import migrations, models
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_auto_20180204_0718'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlideShowImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', sorl.thumbnail.fields.ImageField(upload_to='slides')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
    ]
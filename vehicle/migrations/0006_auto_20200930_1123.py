# Generated by Django 3.1.1 on 2020-09-30 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0005_auto_20200930_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicletype',
            name='slug',
            field=models.SlugField(blank=True, default='', max_length=200, null=True),
        ),
    ]

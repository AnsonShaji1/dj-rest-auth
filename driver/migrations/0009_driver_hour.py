# Generated by Django 3.1.1 on 2020-11-11 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('driver', '0008_remove_driver_hour'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='hour',
            field=models.TimeField(blank=True, null=True),
        ),
    ]

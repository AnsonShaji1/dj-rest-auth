# Generated by Django 3.1.1 on 2020-09-22 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_auto_20200915_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='travel_time',
            field=models.FloatField(blank=True, null=True),
        ),
    ]

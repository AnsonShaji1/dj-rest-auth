# Generated by Django 3.1.1 on 2020-11-25 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0008_project_travel_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]

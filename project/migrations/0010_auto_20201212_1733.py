# Generated by Django 3.1.1 on 2020-12-12 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0009_auto_20201125_2129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]

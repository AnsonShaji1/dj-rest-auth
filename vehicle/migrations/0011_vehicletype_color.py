# Generated by Django 3.1.1 on 2020-11-29 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0010_auto_20201125_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicletype',
            name='color',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
    ]

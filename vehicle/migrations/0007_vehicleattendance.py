# Generated by Django 3.1.1 on 2020-11-02 15:48

import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0006_auto_20200930_1123'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleAttendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('vehicle', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='vehicle.vehicle')),
            ],
        ),
    ]

# Generated by Django 3.1.1 on 2020-11-03 22:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dispatch', '0012_remove_dispatch_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='DispatchStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=40, null=True, unique=True)),
                ('slug', models.SlugField(blank=True, default='', max_length=200, null=True)),
                ('color', models.CharField(blank=True, max_length=40, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='stackstatus',
            name='color',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AddField(
            model_name='dispatch',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dispatch.dispatchstatus'),
        ),
    ]
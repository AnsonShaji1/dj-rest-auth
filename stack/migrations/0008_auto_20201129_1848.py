# Generated by Django 3.1.1 on 2020-11-29 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stack', '0007_stacktype_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stacktype',
            name='color',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]

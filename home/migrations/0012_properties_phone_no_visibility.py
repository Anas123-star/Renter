# Generated by Django 4.1.9 on 2023-07-04 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_alter_properties_latitude_alter_properties_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='properties',
            name='phone_no_visibility',
            field=models.BooleanField(default=True),
        ),
    ]

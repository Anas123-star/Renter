# Generated by Django 4.1.9 on 2023-06-13 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_remove_tenant_rent_collect'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='rent_collect',
            field=models.IntegerField(default=1),
        ),
    ]

# Generated by Django 3.2.7 on 2021-12-22 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esp', '0006_auto_20211213_2145'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalprogramregistration',
            name='checked_in',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='programregistration',
            name='checked_in',
            field=models.BooleanField(default=False),
        ),
    ]

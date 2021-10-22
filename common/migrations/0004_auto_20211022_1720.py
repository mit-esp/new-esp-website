# Generated by Django 3.2.7 on 2021-10-22 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_auto_20211021_2018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaluser',
            name='user_type',
            field=models.CharField(choices=[('admin', 'Admin'), ('teacher', 'Volunteer Teacher'), ('student', 'Student (Grade 7-12)'), ('guardian', 'Guardian of Student'), ('onsite_volunteer', 'On-site Volunteer')], max_length=128),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('admin', 'Admin'), ('teacher', 'Volunteer Teacher'), ('student', 'Student (Grade 7-12)'), ('guardian', 'Guardian of Student'), ('onsite_volunteer', 'On-site Volunteer')], max_length=128),
        ),
    ]

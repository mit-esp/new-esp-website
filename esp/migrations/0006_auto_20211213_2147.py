# Generated by Django 3.2.7 on 2021-12-13 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esp', '0005_coursesection_unique_course_section'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalprogramregistrationstep',
            name='step_key',
            field=models.CharField(choices=[('verify_profile', 'Verify Profile Information'), ('submit_waivers', 'Submit Waivers'), ('time_availability', 'Time Availability'), ('lottery_preferences', 'Lottery Preferences'), ('submit_registration', 'Submit Registration'), ('view_assigned_courses', 'Confirm Assigned Courses'), ('pay_program_fees', 'Payment'), ('complete_surveys', 'Complete Surveys')], max_length=256),
        ),
        migrations.AlterField(
            model_name='programregistrationstep',
            name='step_key',
            field=models.CharField(choices=[('verify_profile', 'Verify Profile Information'), ('submit_waivers', 'Submit Waivers'), ('time_availability', 'Time Availability'), ('lottery_preferences', 'Lottery Preferences'), ('submit_registration', 'Submit Registration'), ('view_assigned_courses', 'Confirm Assigned Courses'), ('pay_program_fees', 'Payment'), ('complete_surveys', 'Complete Surveys')], max_length=256),
        ),
    ]
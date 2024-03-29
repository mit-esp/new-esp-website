# Generated by Django 3.2.16 on 2023-11-07 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esp', '0018_auto_20230101_2008'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='historicalclasspreference',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical class preference', 'verbose_name_plural': 'historical class preferences'},
        ),
        migrations.AlterModelOptions(
            name='historicalclassregistration',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical class registration', 'verbose_name_plural': 'historical class registrations'},
        ),
        migrations.AlterModelOptions(
            name='historicalclassroom',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical classroom', 'verbose_name_plural': 'historical classrooms'},
        ),
        migrations.AlterModelOptions(
            name='historicalclassroomconstraint',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical classroom constraint', 'verbose_name_plural': 'historical classroom constraints'},
        ),
        migrations.AlterModelOptions(
            name='historicalclassroomtag',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical classroom tag', 'verbose_name_plural': 'historical classroom tags'},
        ),
        migrations.AlterModelOptions(
            name='historicalclassroomtimeslot',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical classroom time slot', 'verbose_name_plural': 'historical classroom time slots'},
        ),
        migrations.AlterModelOptions(
            name='historicalcomment',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical comment', 'verbose_name_plural': 'historical comments'},
        ),
        migrations.AlterModelOptions(
            name='historicalcompletedform',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical completed form', 'verbose_name_plural': 'historical completed forms'},
        ),
        migrations.AlterModelOptions(
            name='historicalcompletedstudentform',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical completed student form', 'verbose_name_plural': 'historical completed student forms'},
        ),
        migrations.AlterModelOptions(
            name='historicalcompletedstudentregistrationstep',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical completed student registration step', 'verbose_name_plural': 'historical completed student registration steps'},
        ),
        migrations.AlterModelOptions(
            name='historicalcompletedteacherform',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical completed teacher form', 'verbose_name_plural': 'historical completed teacher forms'},
        ),
        migrations.AlterModelOptions(
            name='historicalcompletedteacherregistrationstep',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical completed teacher registration step', 'verbose_name_plural': 'historical completed teacher registration steps'},
        ),
        migrations.AlterModelOptions(
            name='historicalcourse',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical course', 'verbose_name_plural': 'historical courses'},
        ),
        migrations.AlterModelOptions(
            name='historicalcoursecategory',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical course category', 'verbose_name_plural': 'historical Course categories'},
        ),
        migrations.AlterModelOptions(
            name='historicalcourseflag',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical course flag', 'verbose_name_plural': 'historical course flags'},
        ),
        migrations.AlterModelOptions(
            name='historicalcoursesection',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical course section', 'verbose_name_plural': 'historical course sections'},
        ),
        migrations.AlterModelOptions(
            name='historicalcourseteacher',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical course teacher', 'verbose_name_plural': 'historical course teachers'},
        ),
        migrations.AlterModelOptions(
            name='historicalexternalprogramform',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical external program form', 'verbose_name_plural': 'historical external program forms'},
        ),
        migrations.AlterModelOptions(
            name='historicalfinancialaidrequest',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical financial aid request', 'verbose_name_plural': 'historical financial aid requests'},
        ),
        migrations.AlterModelOptions(
            name='historicalpreferenceentrycategory',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical preference entry category', 'verbose_name_plural': 'historical preference entry categorys'},
        ),
        migrations.AlterModelOptions(
            name='historicalpreferenceentryround',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical preference entry round', 'verbose_name_plural': 'historical preference entry rounds'},
        ),
        migrations.AlterModelOptions(
            name='historicalprogram',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical program', 'verbose_name_plural': 'historical programs'},
        ),
        migrations.AlterModelOptions(
            name='historicalprogramconfiguration',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical program configuration', 'verbose_name_plural': 'historical program configurations'},
        ),
        migrations.AlterModelOptions(
            name='historicalprogramstage',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical program stage', 'verbose_name_plural': 'historical program stages'},
        ),
        migrations.AlterModelOptions(
            name='historicalprogramtag',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical program tag', 'verbose_name_plural': 'historical program tags'},
        ),
        migrations.AlterModelOptions(
            name='historicalpurchaseableitem',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical purchaseable item', 'verbose_name_plural': 'historical purchaseable items'},
        ),
        migrations.AlterModelOptions(
            name='historicalpurchaselineitem',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical purchase line item', 'verbose_name_plural': 'historical purchase line items'},
        ),
        migrations.AlterModelOptions(
            name='historicalstudentavailability',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical student availability', 'verbose_name_plural': 'historical student availabilitys'},
        ),
        migrations.AlterModelOptions(
            name='historicalstudentprofile',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical student profile', 'verbose_name_plural': 'historical student profiles'},
        ),
        migrations.AlterModelOptions(
            name='historicalstudentprogramregistrationstep',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical student program registration step', 'verbose_name_plural': 'historical student program registration steps'},
        ),
        migrations.AlterModelOptions(
            name='historicalstudentregistration',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical student registration', 'verbose_name_plural': 'historical student registrations'},
        ),
        migrations.AlterModelOptions(
            name='historicalteacheravailability',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical teacher availability', 'verbose_name_plural': 'historical teacher availabilitys'},
        ),
        migrations.AlterModelOptions(
            name='historicalteacherprofile',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical teacher profile', 'verbose_name_plural': 'historical teacher profiles'},
        ),
        migrations.AlterModelOptions(
            name='historicalteacherprogramregistrationstep',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical teacher program registration step', 'verbose_name_plural': 'historical teacher program registration steps'},
        ),
        migrations.AlterModelOptions(
            name='historicalteacherregistration',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical teacher registration', 'verbose_name_plural': 'historical teacher registrations'},
        ),
        migrations.AlterModelOptions(
            name='historicaltimeslot',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical time slot', 'verbose_name_plural': 'historical time slots'},
        ),
        migrations.AlterModelOptions(
            name='historicaluserpayment',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical user payment', 'verbose_name_plural': 'historical user payments'},
        ),
        migrations.AlterField(
            model_name='historicalclasspreference',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalclassregistration',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalclassroom',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalclassroomconstraint',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalclassroomtag',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalclassroomtimeslot',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalcomment',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalcompletedform',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalcompletedstudentform',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalcompletedstudentregistrationstep',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalcompletedteacherform',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalcompletedteacherregistrationstep',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalcourse',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalcoursecategory',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalcourseflag',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalcoursesection',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalcourseteacher',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalexternalprogramform',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalfinancialaidrequest',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalpreferenceentrycategory',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalpreferenceentryround',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalprogram',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalprogramconfiguration',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalprogramstage',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalprogramtag',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalpurchaseableitem',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalpurchaselineitem',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalstudentavailability',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalstudentprofile',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalstudentprogramregistrationstep',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalstudentregistration',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalteacheravailability',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalteacherprofile',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalteacherprogramregistrationstep',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicalteacherregistration',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicaltimeslot',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='historicaluserpayment',
            name='history_date',
            field=models.DateTimeField(db_index=True),
        ),
    ]

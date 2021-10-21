# Generated by Django 3.2.7 on 2021-10-21 20:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('esp', '0004_auto_20211021_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursetag',
            name='display_name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='coursetag',
            name='is_category',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalcoursetag',
            name='display_name',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='historicalcoursetag',
            name='is_category',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='classpreference',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='classroom',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='classroomavailability',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='classroomresource',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='classsection',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='completedregistrationstep',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='course',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='coursetag',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalclasspreference',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalclassroom',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalclassroomavailability',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalclassroomresource',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalclasssection',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalcompletedregistrationstep',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalcourse',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalcoursetag',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalpermission',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalpreferenceentrycategory',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalpreferenceentryconfiguration',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalpreferenceentryround',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalprogram',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalprogramregistration',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalprogramregistrationstep',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalprogramstage',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalprogramtag',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalresourcerequest',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalresourcetype',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicalstudentprofile',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='historicaltimeslot',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='permission',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='preferenceentrycategory',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='preferenceentryconfiguration',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='preferenceentryround',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='program',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='programregistration',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='programregistrationstep',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='programstage',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='programtag',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='resourcerequest',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='resourcetype',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='timeslot',
            name='is_deleted',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.CreateModel(
            name='TeacherProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('mit_affiliation', models.CharField(choices=[('undergrad', 'Undergraduate Student'), ('grad', 'Graduate Student'), ('postdoc', 'Postdoctoral Student'), ('other', 'Other'), ('', 'None')], max_length=32, verbose_name='What is your affiliation with MIT?')),
                ('major', models.CharField(blank=True, help_text='If you are currently a student, please provide your major or degree field.', max_length=128, null=True)),
                ('graduation_year', models.CharField(blank=True, help_text='If you are currently a student, please provide your graduation year.', max_length=4, null=True)),
                ('university_or_employer', models.CharField(blank=True, help_text='If you are not affiliated with MIT, please provide your university or employer.', max_length=128, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('shirt_size', models.CharField(choices=[('XXS', 'Xxs'), ('XS', 'Xs'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'Xl'), ('XXL', 'Xxl')], max_length=3)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='teacher_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalTeacherProfile',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('updated_on', models.DateTimeField(blank=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('mit_affiliation', models.CharField(choices=[('undergrad', 'Undergraduate Student'), ('grad', 'Graduate Student'), ('postdoc', 'Postdoctoral Student'), ('other', 'Other'), ('', 'None')], max_length=32, verbose_name='What is your affiliation with MIT?')),
                ('major', models.CharField(blank=True, help_text='If you are currently a student, please provide your major or degree field.', max_length=128, null=True)),
                ('graduation_year', models.CharField(blank=True, help_text='If you are currently a student, please provide your graduation year.', max_length=4, null=True)),
                ('university_or_employer', models.CharField(blank=True, help_text='If you are not affiliated with MIT, please provide your university or employer.', max_length=128, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('shirt_size', models.CharField(choices=[('XXS', 'Xxs'), ('XS', 'Xs'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'Xl'), ('XXL', 'Xxl')], max_length=3)),
                ('history_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical teacher profile',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalClassRegistration',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ('created_on', models.DateTimeField(blank=True, editable=False)),
                ('updated_on', models.DateTimeField(blank=True, editable=False)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('created_by_lottery', models.BooleanField()),
                ('confirmed_on', models.DateTimeField(null=True)),
                ('history_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('class_section', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='esp.classsection')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('program_registration', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='esp.programregistration')),
            ],
            options={
                'verbose_name': 'historical class registration',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='ClassRegistration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False, editable=False)),
                ('created_by_lottery', models.BooleanField()),
                ('confirmed_on', models.DateTimeField(null=True)),
                ('class_section', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='registrations', to='esp.classsection')),
                ('program_registration', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='class_registrations', to='esp.programregistration')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

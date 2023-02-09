# Base image
FROM ubuntu:focal

# Setup working directory
RUN mkdir /app
WORKDIR /app
COPY ./code /app

# Set environment variables
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONBUFFERED 1

# Install packages
RUN apt update ; apt upgrade -y ; apt install -y python3-dev python3-pip libpq-dev npm; ln -s /usr/bin/python3 /usr/bin/python; pip install -r requirements.txt ; npm install ; python manage.py migrate

EXPOSE 8000

# Inject dummy accounts
RUN echo "from django.contrib.auth import get_user_model; \
    User = get_user_model(); \
    User.objects.create_superuser( \
        username='admin', \
        email='admin@esp.mit.edu', \
        password='password' \
    )" | python manage.py shell
RUN echo "from django.contrib.auth import get_user_model; \
    from common.constants import UserType; \
    from esp.models.program_registration_models import TeacherProfile; \
    User_t = get_user_model(); \
    user_t = User_t.objects.create_user( \
        username='teacher', \
        email='teacher@esp.mit.edu', \
        password='password', \
        user_type=UserType.teacher \
    ); \
    prof_t = TeacherProfile.objects.create( \
        user=user_t, cell_phone='555-555-5555', \
        mit_affiliation='undergrad', major='6-9', \
        graduation_year=2026, shirt_size='S' \
    )" | python manage.py shell
RUN echo "from django.contrib.auth import get_user_model; \
    from common.constants import UserType; \
    from esp.models.program_registration_models import StudentProfile; \
    import datetime; \
    User_s = get_user_model(); \
    user_s = User_s.objects.create_user( \
        username='student', \
        email='student@esp.mit.edu', \
        password='password', \
        user_type=UserType.student \
    ); \
    prof_s = StudentProfile.objects.create( \
        user=user_s, \
        address_street='77 Mass Ave', \
        address_city='Cambridge', \
        address_state='MA', \
        address_zip='02169', \
        home_phone='123-456-7890', \
        cell_phone='555-555-5555', \
        dob=datetime.date(2008, 1, 1), \
        graduation_year=2026, \
        school='Edward S. Pembroke High School', \
        heard_about_esp_via='teacher', \
        guardian_first_name='Alyssa', \
        guardian_last_name='Hacker', \
        guardian_email='aphacker@mit.edu', \
        guardian_home_phone='123-456-7890', \
        guardian_cell_phone='555-555-5555', \
        emergency_contact_first_name='Alyssa', \
        emergency_contact_last_name='Hacker', \
        emergency_contact_email='aphacker@mit.edu', \
        emergency_contact_address_street='77 Mass Ave', \
        emergency_contact_address_city='Cambridge', \
        emergency_contact_address_state='MA', \
        emergency_contact_address_zip='02169', \
        emergency_contact_home_phone='123-456-7890', \
        emergency_contact_cell_phone='555-555-5555' \
    )" | python manage.py shell
RUN echo "from esp.models.program_models import Course, CourseCategory, CourseFlag, Program, ProgramConfiguration, ProgramStage, TimeSlot; \
    from datetime import datetime, timedelta, timezone; \
    timezone_est = timezone(timedelta(hours=-5)); \
    config = ProgramConfiguration.objects.create( \
        saved_as_preset=False, \
        name='config0', \
        description='sample configuration' \
    ); \
    program = Program.objects.create( \
        program_configuration=config, \
        name='Summer HSSP 2023', \
        program_type='hssp', \
        min_grade_level=7, \
        max_grade_level=12, \
        description='A 6-week program', \
        start_date=datetime(2023, 7, 9, 0, 0, 0, 0, timezone_est), \
        end_date=datetime(2023, 8, 13, 23, 59, 59, 999999, timezone_est), \
        number_of_weeks=6, \
        time_block_minutes=30 \
    ); \
    program_stage = ProgramStage.objects.create( \
        program=program, \
        name='Lottery Preferences', \
        start_date=datetime(2023, 2, 8, 0, 0, 0, 0, timezone_est), \
        end_date=datetime(2023, 4, 9, 13, 0, 0, 0, timezone_est) \
    ); \
    timeslots = [ \
        TimeSlot.objects.create( \
            program=program, \
            start_datetime=datetime(2023, 7, 9, 13, 0, 0, 0, timezone_est), \
            end_datetime=datetime(2023, 7, 9, 13, 29, 59, 999999, timezone_est) \
        ), \
        TimeSlot.objects.create( \
            program=program, \
            start_datetime=datetime(2023, 7, 9, 13, 30, 0, 0, timezone_est), \
            end_datetime=datetime(2023, 7, 9, 13, 59, 59, 999999, timezone_est) \
        ), \
        TimeSlot.objects.create( \
            program=program, \
            start_datetime=datetime(2023, 7, 9, 14, 0, 0, 0, timezone_est), \
            end_datetime=datetime(2023, 7, 9, 14, 29, 59, 999999, timezone_est) \
        ), \
        TimeSlot.objects.create( \
            program=program, \
            start_datetime=datetime(2023, 7, 9, 14, 30, 0, 0, timezone_est), \
            end_datetime=datetime(2023, 7, 9, 14, 59, 59, 999999, timezone_est) \
        ), \
        TimeSlot.objects.create( \
            program=program, \
            start_datetime=datetime(2023, 7, 9, 15, 0, 0, 0, timezone_est), \
            end_datetime=datetime(2023, 7, 9, 15, 29, 59, 999999, timezone_est) \
        ), \
        TimeSlot.objects.create( \
            program=program, \
            start_datetime=datetime(2023, 7, 9, 15, 30, 0, 0, timezone_est), \
            end_datetime=datetime(2023, 7, 9, 15, 59, 59, 999999, timezone_est) \
        ), \
    ]; \
    categories = [ \
        CourseCategory.objects.create( \
            display_name='Computer Science', \
            symbol='C', \
            current=True \
        ), \
    ]; \
    flag = CourseFlag.objects.create( \
        display_name='No teacher with kerb', \
        show_in_dashboard=True, \
        show_in_scheduler=True \
    ); \
    course = Course.objects.create( \
        program=program, \
        name='How to Make a Website', \
        category=categories[0], \
        description='This class will cover the Django framework for creating websites, like the one you are currently on :)', \
        max_section_size=50, \
        max_sections=1, \
        time_slots_per_session=2, \
        number_of_weeks=6, \
        sessions_per_week=1, \
        prerequisites='None', \
        min_grade_level=7, \
        max_grade_level=12, \
        difficulty=2, \
        status='unreviewed' \
    );" | python manage.py shell

# Start server
CMD python manage.py runserver 0.0.0.0:8000

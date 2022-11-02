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

# Inject admin account
RUN echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser(username='admin', email='admin@esp.mit.edu', password='password')" | python manage.py shell
RUN echo "from django.contrib.auth import get_user_model; from common.constants import UserType; User_t = get_user_model(); user_t = User_t.objects.create_user(username='teacher', email='teacher@esp.mit.edu', password='password', user_type=UserType.teacher);" | python manage.py shell
RUN echo "from django.contrib.auth import get_user_model; from common.constants import UserType; User_s = get_user_model(); user_s = User_s.objects.create_user(username='student', email='student@esp.mit.edu', password='password', user_type=UserType.student);" | python manage.py shell

# Start server
CMD python manage.py runserver 0.0.0.0:8000

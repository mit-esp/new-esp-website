# MIT ESP
Previous code repository: https://github.com/learning-unlimited/ESP-Website/tree/mit-prod

A website to help manage the logistics of large short-term educational programs. This website was written by the [MIT Educational Studies Program](https://esp.mit.edu) to support [Splash](https://esp.mit.edu/learn/Splash) and other educational programs.


## Local Project Setup
```
# Create environment config file.
cp config/.env.example config/.env

# Fill in appropriate environment values.
vim config/.env
# set top level REACT_APP_API_BASE_URL to backend API base url
vim .env

# Install backend requirements.
pip install -r requirements.txt

# Install frontend requirements.
npm install

# Apply migrations and sync database schema.
python manage.py migrate

# To run the project:
python manage.py runserver_plus

#To run the React scheduler in development:
npm run start
```

To access the database:
```
python manage.py shell_plus
```
To run the test suite:
```
python manage.py test
```
To get a test coverage report:
```
coverage run --source='.' manage.py test; coverage report
```
To run auto formatter(s) and style checks:
```
pre-commit run --all-files
```
To add a new dependency to or update requirements, add the entry to requirements.in and run `pip-compile` to generate requirements.txt:
```
vim requirements.in  # Updating Python dependencies as needed
pip-compile --upgrade  # Generate requirements.txt with updated dependencies
```


# Deployment
Install Postgres:
```buildoutcfg
sudo yum install -y postgresql-devel
```

Configure environment variables in `config/.env` (backend environment variables file) e.g.
```
HOST=esp-dev.mit.edu
DEBUG=False
DEBUG_TOOLBAR=False
LOCALHOST=False
...
```
and `.env` (frontend environment variables file) e.g.
```
REACT_APP_API_BASE_URL=https://esp-dev.mit.edu
```

Deployment commands:
```
git pull
pip install --upgrade pip
pip install -r requirements.txt
npm install
npm run build
python manage.py compilescss
python manage.py collectstatic --noinput --ignore *.scss
python manage.py migrate --noinput

# restart wsgi process e.g.
sudo systemctl restart gunicorn
```

### Settings

`MAINTENANCE_MODE`: Set this flag on a server environment to stop all user requests to the site, such as when you need to make substantial server updates or run a complex database migration.


### Running an ESP Program
1. As Admin, create a Program object
2. As Admin, add ProgramStages with the dates that each stage should start and end (e.g. "pre-lottery stage", "post-lottery stage")
3. As Admin, add ProgramRegistrationSteps to each stage (In Django Admin Panel, go to Programs to create objects). Some steps must exist and be coherently ordered.
4. As Admin, add TeacherRegistrationSteps (teacher registration steps) (in Django Admin Panel).
5. As Admin, add external program forms (in Django Admin Panel)
6. As Admin, add purchasable items (In Django Admin Panel)
7. As Admin, create/add classrooms if they don’t already exist from previous Programs (in Django Admin Panel)
8. As Admin, create classroom time slots for times classrooms are available
9. Teachers and Students submit waivers, if waivers are a ProgramRegistrationStep
10. Teachers create classes and submit time availability, teachers add co-teachers
11. Admins approve classes and create the desired number of sections (From `manage courses` action)
12. As Admin, schedule course sections to classroom timeslots via Scheduler
13. Teachers confirm course section time slots, (missing)
14. Students enter lottery preferences
15. As Admin, run lottery
16. Students confirm their courses (missing)
17. Teachers can see how many students signed up with their courses (missing)
18. Day-of: Students check in for the program
19. Day-of: Teachers check in before each hour of courses


<!--
### Documentation
Documentation for program administrators and developers is in the docs directory, including dev setup documentation and instructions for contributors.

After installing Sphinx via `pip install sphinx`:
```
# sphinx-apidoc -o . ..
make html
make linkcheck
```
 -->
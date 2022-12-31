# MIT ESP
Previous code repository: https://github.com/learning-unlimited/ESP-Website/tree/mit-prod

A website to help manage the logistics of large short-term educational programs. This website was written by the [MIT Educational Studies Program](https://esp.mit.edu) to support [Splash](https://esp.mit.edu/learn/Splash) and other educational programs.

**Check out the README in the root directory**


## Local Project Setup
```
# Create environment config file.
cp config/.env.example config/.env

# Fill in appropriate environment values here later. Skip for now.
vim config/.env
# set top level REACT_APP_API_BASE_URL to backend API base url later. Skip for now.
vim .env

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend requirements.
# ‘apt’ is for Ubuntu systems,
# use whatever package manager your OS uses.
sudo apt install libpq-dev python3-dev
pip install wheel
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

Install System dependencies (operating system dependent):
- To generate LaTeX-based printables, `pdflatex` needs to be installed and callable: https://www.tug.org/texlive/quickinstall.html


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


## Program Run Guide (WIP) 

Here are the steps one should take in order to run an ESP program on this system.
1. As an Admin user, create a Program object. Tag with ProgramTags as desired.
2. As an Admin user, add ProgramStages with the dates that each stage should start and end (e.g. "pre-lottery stage", "post-lottery stage")
3. As an Admin user, add StudentProgramRegistrationSteps to each stage (In Django Admin Panel, go to Programs to create objects). Be very careful with this step, as while the system allows the free rein of customized ordering, certain steps are expected be coherently ordered.
4. As an Admin user, add TeacherRegistrationSteps (teacher registration steps) (in Django Admin Panel).
5. As an Admin user, add ExternalProgramForms (in Django Admin Panel)
6. As an Admin user, add PurchaseableItems (In Django Admin Panel)
7. As an Admin user, create/add classrooms if they don’t already exist from previous Programs (in Django Admin Panel), and modify ClassroomTags as desired
8. As an Admin user, create ClassroomTimeSlots for the times that classrooms are available for the Program
9. Teachers create proposed Courses, submit their time availability, and add co-teachers
10. As an Admin user, approve Courses and create the desired number of sections (on the `manage courses` page)
11. As an Admin user, schedule course sections to classroom timeslots via the Scheduler
12. Teachers confirm CourseSection time slots
13. Students enter lottery preferences
14. As an Admin user, run the lottery process
15. Students confirm their courses, and Teachers can view how many students signed up with their courses
16. Students and Teachers check in for the Program day-of


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

# MIT ESP new website
Previous code repository: https://github.com/learning-unlimited/ESP-Website/tree/mit-prod

A website to help manage the logistics of large short-term educational programs. This website was written by the [MIT Educational Studies Program](https://esp.mit.edu) to support [Splash](https://esp.mit.edu/learn/Splash) and other educational programs.

Documentation and setup instructions can be found at https://esp.mit.edu/espider-docs.

# Setup

Before setup, clone this repo, create a branch for yourself, and checkout into that branch:

```
git clone git@github.com:mit-esp/new-esp-website.git
cd new-esp-website
git checkout -b dev-[your name]
git push -u origin dev-[your name] (push your new branch to github)
```

File paths in these instructions are relative with respect to the repo's home directory.

### Docker Setup
Docker containers are a way to create/store environments to run programs consistently.

First, install Docker via whichever method your OS uses.

Once Docker is installed:
```
# Create the environment file, fill in values later
cp code/config/.env.example code/config/.env
```

To view your copy of the website:
```
# Build and run the docker file
docker build . -t espdev
docker run -itp 8000:8000 espdev

# Press Ctrl+C to exit.
```
Depending on how you installed Docker, you may need to run these in `sudo` mode.

Then, go to `localhost:8000` in your browser to see the website.

### Local Project Setup
```
# cd into the /code folder
# Create environment config file.
cp config/.env.example config/.env

# Fill in appropriate environment values here later. Skip for now.
vim config/.env

# Set top level REACT_APP_API_BASE_URL to backend API base url later. Skip for now.
vim .env

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate
```

Install backend requirements.
- Ubuntu systems:
```
sudo apt install libpq-dev python3-dev
```
- MacOS (must have Homebrew installed):
```
brew install libpq python3
```

```
# Install other backend requirements:
pip install wheel
pip install -r requirements.txt

# Install frontend requirements.
npm install

# Apply migrations and sync database schema.
python manage.py migrate
```

### Setting up postgresql for development

1. [Download](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) and install PostgreSQL. Use all of the default settings.
2. When setting up PostgreSQL, you will be prompted to create a password for the default database superuser (postgres), remember this password.
3. Open pgAdmin (which comes with the installation if everything goes right), and set some passwords when prompted.
4. On the left panel, right click on databases and create a new database. The name of the database should be 'espmit-database', others can be left as default.
5. Go to code/config/settings.py, find a JSON string called DATABASES, and change the password value to your password.
6. In a terminal, cd into the code file.
7. Run the following to create the empty database. You should see a datadump.json being created but you can ignore it.
```
python manage.py makemigrations
python manage.py migrate
```
8. In pgAdmin, go to the table 'common_user' in espmit-database/Schemas/public/Tables/common_user, right click on the left and "Import/Export Data". Go to Options and turn on Header, then import the csv file called SampleUserData.csv located in the root directory.

Account type | Username | Password
-------------|----------|----------------
   Admin     | admin    | adminpassword
   Teacher   | teacher  | teacherpassword
   Student   | student  | studentpassword

# Running a local copy

To run the project:
```
cd code
python manage.py runserver_plus
```

To run the React scheduler in development:
```
cd code
npm run start
```

Install System dependencies (operating system dependent):
- To generate LaTeX-based printables, `pdflatex` needs to be installed and callable: https://www.tug.org/texlive/quickinstall.html


To access the database:
```
cd code
python manage.py shell_plus
```
To run the test suite:
```
cd code
python manage.py test
```
To get a test coverage report:
```
cd code
coverage run --source='.' manage.py test; coverage report
```
To run auto formatter(s) and style checks:
```
cd code
pre-commit run --all-files
```
To add a new dependency to or update requirements, add the entry to requirements.in and run `pip-compile` to generate requirements.txt:
```
cd code
vim requirements.in  # Updating Python dependencies as needed
pip-compile --upgrade  # Generate requirements.txt with updated dependencies
```


# Deployment
Install Postgres:
```buildoutcfg
sudo yum install -y postgresql-devel
```

Configure environment variables in `code/config/.env` (backend environment variables file) e.g.
```
HOST=esp-dev.mit.edu
DEBUG=False
DEBUG_TOOLBAR=False
LOCALHOST=False
...
```
and `code/.env` (frontend environment variables file) e.g.
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


## Navigation
Information will not be saved in between Docker runs.

### Login information
Account type | Username | Password
-------------|----------|----------
   Admin     | admin    | password
   Teacher   | teacher  | password
   Student   | student  | password



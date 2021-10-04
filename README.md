# MIT ESP
Previous code repository: https://github.com/learning-unlimited/ESP-Website/tree/mit-prod

A website to help manage the logistics of large short-term educational programs. This website was written by the [MIT Educational Studies Program](https://esp.mit.edu) to support [Splash](https://esp.mit.edu/learn/Splash) and other educational programs.

<!-- Documentation for program administrators and developers is in the docs directory, including dev setup documentation and instructions for contributors. -->

## Local Project Setup
```
# Create environment config file.
cp config/.env.example config/.env

# Fill in appropriate environment values.
vim config/.env

# Install pip requirements.
pip install -r requirements.txt

# Apply migrations and sync database schema.
python manage.py migrate

# Creates database fixtures.
python manage.py loaddata --app common fixtures.json
```

To run the project:
```
python manage.py runserver_plus
```
To access the database:
```
python manage.py shell_plus
```
To run test suite:
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

Deployment commands
```
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput --ignore *.scss
```

### Settings

`MAINTENANCE_MODE`: Set this flag on a server environment to stop all user requests to the site, such as when you need to make substantial server updates or run a complex database migration.


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

Configure environment variables in `.env` and `config/.env`

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


### Documentation
After installing Sphinx via `pip install sphinx`:
```
# sphinx-apidoc -o . ..
make html
make linkcheck
```

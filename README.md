# MIT ESP
Previous code repository: https://github.com/learning-unlimited/ESP-Website/tree/mit-prod

A website to help manage the logistics of large short-term educational programs. This website was written by the [MIT Educational Studies Program](https://esp.mit.edu) to support [Splash](https://esp.mit.edu/learn/Splash) and other educational programs.

## Pre-setup
Before setup, clone this repo. File paths in these instructions are relative with respect to the repo's home directory.

## Docker Setup
[blurb about using Docker]
First, install Docker via whichever method your OS uses.
```
# Create the environment file, fill in values later
cp code/config/.env.example code/config/.env

# Build and run the docker file
docker build . -t espdev
docker run -itp 8000:8000 espdev

# Press Ctrl+C to exit.
```
Go to `localhost:8000` in your browser to see the website.

## Local Setup
To keep a copy of the website outside of Docker:
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

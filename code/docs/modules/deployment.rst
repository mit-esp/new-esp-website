##########
Deployment
##########

These are instructions for deploying the website from GitHub to esp-dev.mit.edu. They may need to be executed as sudo.

SSH into the ``esp-dev.mit.edu`` server with username ``esp``, and go to the ``/esp`` folder.

Install Postgres:

.. code-block::

    sudo apt install -y postgresql

Copy files from the ``code`` folder in the latest version of the repository to the ``/esp`` folder.

Make sure the ``config/.env`` file matches ``config/.env.deployment``, and the ``.env`` (frontend environment variables file) contains

.. code-block::

    REACT_APP_API_BASE_URL=https://esp-dev.mit.edu

Deployment commands:

.. code-block::

    pip install --upgrade pip
    pip install -r requirements.txt
    npm install
    npm run build
    python manage.py compilescss
    python manage.py collectstatic --noinput --ignore *.scss
    python manage.py migrate --noinput

    # restart wsgi process e.g.
    sudo systemctl restart gunicorn

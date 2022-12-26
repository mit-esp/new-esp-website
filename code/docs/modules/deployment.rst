##########
Deployment
##########

These are instructions for deploying the website from GitHub to esp-dev.mit.edu. They may need to be executed as sudo.

Pre-deployment
==============

SSH into the ``esp-dev.mit.edu`` server with username ``esp``, and go to the ``/esp`` folder.

Dependencies (probably not necessary):

.. code-block::

    sudo apt install -y postgresql
    pip install --upgrade pip
    pip install -r requirements.txt

Copy files from the ``code`` folder in the latest version of the repository to the ``/esp`` folder.

Make sure the ``config/.env`` file matches ``config/.env.deployment``, and the ``.env`` in the ``/esp`` folder (frontend environment variables file) contains

.. code-block::

    REACT_APP_API_BASE_URL=https://esp-dev.mit.edu

Deployment commands
===================

.. code-block::

    npm install
    npm run build
    python manage.py compilescss
    python manage.py collectstatic --noinput --ignore *.scss
    python manage.py migrate --noinput

    # restart wsgi process e.g.
    sudo systemctl restart gunicorn

After deployment
================

Changes should be propagated more or less immediately.

If a new model was created, it may be necessary to enable non-superusers to make changes to this model through the admin panel.

One way to do this (for users in the "All permissions allowed" group): go to ``Groups > All Permissions Allowed`` on the admin panel, and carry over permissions from the left column to the right.
##########
Deployment
##########

These are instructions for deploying the website from GitHub to esp-dev.mit.edu.

Install Postgres:

.. code-block::

    sudo apt install -y postgresql

or

.. code-block::

    sudo yum install -y postgresql-devel

Configure environment variables in ``config/.env`` (backend environment variables file) e.g.

.. code-block::

    HOST=esp-dev.mit.edu
    DEBUG=False
    DEBUG_TOOLBAR=False
    LOCALHOST=False
    ...

and ``.env`` (frontend environment variables file) e.g.

.. code-block::

    REACT_APP_API_BASE_URL=https://esp-dev.mit.edu

Deployment commands:

.. code-block::

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

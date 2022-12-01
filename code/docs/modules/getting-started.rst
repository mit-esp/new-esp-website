###############
Getting started
###############

Setup
=====

Before setup, clone this repo. File paths in these instructions are relative with respect to the repo's home directory.

Docker Setup
------------

Docker containers are a way to create/store environments to run programs consistently.

First, install Docker via whichever method your OS uses.

Once Docker is installed:

.. code-block::

    # Create the environment file, fill in values later
    cp code/config/.env.example code/config/.env

To view your copy of the website:

.. code-block::

    # Build and run the docker file
    docker build . -t espdev
    docker run -itp 8000:8000 espdev

    # Press Ctrl+C to exit.

Depending on how you installed Docker, you may need to run these in ``sudo`` mode.

Then, go to ``localhost:8000`` in your browser to see the website.

Additional local setup
----------------------

I (songk) have a separate conda environment for this. I haven't experimented with other venvs.


Navigating the website
======================

Note: Information will not be saved in between Docker runs.

Login information
-----------------

The Docker image comes with a few dummy accounts to access different parts of the website. The admin account also has teacher and student capabilities.

+--------------+----------+----------+
| Account type | Username | Password |
+==============+==========+==========+
|    Admin     | admin    | password |
+--------------+----------+----------+
|    Teacher   | teacher  | password |
+--------------+----------+----------+
|    Student   | student  | password |
+--------------+----------+----------+

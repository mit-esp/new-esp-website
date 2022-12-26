###############
Getting started
###############

Setup
=====

Before setup, clone this repo, create a branch for yourself, and checkout into that branch. This compartmentalizes your changes to the codebase.

.. code-block::

    git clone https://github.com/mit-esp/new-esp-website.git
    cd new-esp-website
    git branch dev-[your name]
    git checkout dev-[your name]

File paths in these instructions are relative with respect to the repo's home directory.

Docker Setup
------------

Docker containers are a way to create/store environments to run programs consistently. The repo comes with a pre-made Docker container that we use to test the website locally.

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

I (songk) have a separate conda environment for this. I haven't tried other venvs but they should work too.

To get the dependencies needed for running the website, compiling documentation, etc. run ``pip install -r requirements.txt``

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

As of right now, the teacher and student profiles associated with each account have to be re-initialized each time.
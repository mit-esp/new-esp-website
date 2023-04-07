###############
Getting started
###############

Setup
=====

Before setup, clone this repo, create a branch for yourself, and checkout into that branch. This compartmentalizes your changes to the codebase.

.. code-block::

    git clone https://github.com/mit-esp/new-esp-website.git
    cd new-esp-website
    git checkout -b dev-[your name]

File paths in these instructions are relative with respect to the repo's home directory.

Docker Setup
------------

Docker containers are a way to create/store environments to run programs consistently. The repo comes with a pre-made Docker container that we use to test the website locally.

First, `install Docker <https://www.docker.com/>` via whichever method your OS uses.

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

songk has a separate conda environment for this. I haven't tried other venvs but they should work too. <!--- TODO: what are venvs how do?? --->

You might need to install some other software before all the pip packages can install. Here's an initial list of what to install (should be tested on a blank environment):

* `Microsoft C++ Build Tools <https://visualstudio.microsoft.com/visual-cpp-build-tools/>` (Install "Desktop development with C++" and check the optional install for "C++ x64/x86 build tools".)
* `PostgreSQL <https://www.postgresql.org/download/>` (Use default options, and don't install the optional stuff at the end.)

To get the dependencies needed for running the website, compiling documentation, etc. run ``pip install -r requirements.txt``. If you run into issues with versions, ask an ESPider director to recompile and update the requirements.txt file. 


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
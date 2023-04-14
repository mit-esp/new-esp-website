## Instructions for setting up postgresql for development
1. [Download](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) and install PostgreSQL. Use all of the default settings.
2. When setting up PostgreSQL, you will be prompted to create a password for the default database superuser (postgres), remember this password.
3. Open pgAdmin (which comes with the installation if everything goes right), and set some passwords when prompted.
4. On the left panel, right click on databases and create a new database. The name of the database should be 'espmit-database', others can be left as default.
5. In a terminal, cd into the code file.
6. Run `python manage.py makemigrations` and then `python manage.py migrate` to create the empty database. You should see a datadump.json being created but you can ignore it.
7. Go to the table 'common_user' in espmit-database/Schemas/public/Tables/common_user, and import the csv file called SampleUserData.csv located in the root directory.

Account type | Username | Password
-------------|----------|----------------
   Admin     | admin    | adminpassword
   Teacher   | teacher  | teacherpassword
   Student   | student  | studentpassword
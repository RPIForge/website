# RPIForge/website
The Forge's website - tracks machine usage and calculates charges for members.

To install the app, you must have a working Python 3.7.x installation and PostgreSQL.

Required Python libraries:

- psycopg2
- argon2-cffi
- django

Recommended:

- bcrypt

The app currently expects a database user `postgresql@localhost:5432` with password `password`. This behavior will be changed shortly to use environment variables to store database credentials. The program also currently expects a `forge_devel` database to have already been created. These settings can be found in `forge/settings.py`.

Before running the app for the first time, you should set up the database through Django. You can do this by running:

	- python manage.py makemigrations
	- python manage.py migrate
	- python manage.py create_superuser
	
Note that `create_superuser` creates a user `admin` with password `password` for development. Don't do this in prod.
	
Afterwards, you can run the app by simply typing:

	- python manage.py runserver

The site will be accessible at localhost:8000 (unless you specify another port as an argument to runserver). To access the Django admin panel, point your browser to localhost:8000/admin. To access the site, go to localhost:8000/machine_usage/. This behavior will soon change to hosting the site at the site root.

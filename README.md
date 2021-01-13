# RPIForge/website 
The Forge's website - tracks machine usage and calculates charges for members.

## Installation
The first step of any install is to clone the repo to your local machine.

### Docker install
To install using docker you must first install [Docker](https://docs.docker.com/get-docker/) and
[Docker-Compose](https://docs.docker.com/compose/install/). Then run the following command to start
up the containers.

	- docker-compose up -d

And then once the containers are up attach to the web container using the following command to the instance

	-  docker-compose exec web bash

### Normal Install
#### Python
To install the app, you must have a working Python 3.7.x installation and PostgreSQL.

Required Python libraries:

- psycopg2
- argon2-cffi
- django
- sendgrid
- google-api

Recommended:

- bcrypt

To automatically install requirements run the following command:

	- pip install -r requirements.txt

#### Postgres
The app currently expects a database user `postgres@localhost:5432` with password `password`. This behavior will be changed shortly to use environment variables to store database credentials. The program also currently expects a `forge_devel` database to have already been created. These settings can be found in `forge/settings.py`. Contact the web mainters if you are having trouble connecting.

## First time setup
Before running the app for the first time, you should set up the database through Django. You can do this by running the following commands. If using docker make sure to connect to the container.

	- python manage.py makemigrations
	- python manage.py migrate
	- python manage.py create_superuser


Afterwards, you can run the app by either restarting the docker-compose or running the following command:

	- python manage.py runserver

The site will be accessible at localhost:8000 (unless you specify another ip or port as an argument to runserver). To access the Django admin panel, point your browser to localhost:8000/admin. To access the site, go to localhost:8000/. 

You will want to initialize the database with some values. First go to `/admin/auth/user/` and select your account. You will want to create and add the following groups
	-admins
	-managers
	-member
	-volunteers
	-verified_email

You will also want to create a machine at `/admin/machine_management/machine/` and create slots for it at `/admin/machine_management/machineslot/`. This will allow you to use the site with full functionality

## Contributing
Take a look at the current issues and the current project to see priorities.

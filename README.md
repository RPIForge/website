# RPIForge/website 
The Forge's website - tracks machine usage and calculates charges for members.

## Installation
The first step of any install is to clone the repo to your local machine.

### Docker install (preferred)
To install using docker you must first install [Docker](https://docs.docker.com/get-docker/) and
[Docker-Compose](https://docs.docker.com/compose/install/). Then run the following command to start
up the containers.

	- docker-compose up -d

And then once the containers are up attach to the web container using the following command to the instance

	-  docker exec  -it forge-web bash

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
The app is currently configured for the docker install and should be changed in `forge/setttings.py`. The main change would be to set the database `hostname` to either `localhost` or the ip of your postgres server.  The app will expect a database user `postgres@hostname:5432` with password `password` and a database called "forge_devel". Contact the web mainters if you are having trouble connecting.

## First time setup
Before running the app for the first time, you should set up the database through Django. You can do this by running the following commands. If using docker make sure to connect to the container.

	- python manage.py makemigrations
	- python manage.py migrate
	- python manage.py createsuperuser


Afterwards, you can run the app by either restarting the docker-compose or running the following command (depending on how you installed):

	- python manage.py runserver

The site will be accessible at localhost:8000 if using the normal install or localhost:80 if using  docker. To access the Django admin panel, point your browser to site/admin. 

You will want to initialize the database with some values. First go to `/admin/auth/user/` and select your account. You will want to create and add the following groups
	-admins
	-managers
	-member
	-volunteers
	-verified_email

You will also want to create a machine at `/admin/machine_management/machine/` and create slots for it at `/admin/machine_management/machineslot/`. This will allow you to use the site with full functionality

## Contributing
Take a look at the current issues and the current project to see priorities.

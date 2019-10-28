# website
The Forge's website - tracks machine usage and calculates charges.

"README coming soon!" -- Famous Last Words

To run the app:
	- python manage.py makemigrations
	- python manage.py migrate
	- python manage.py runserver

Expects a PostgreSQL server running on localhost. For development, the database 'forge_devel' and credentials 'postgres'/'password' are used.
These can be configured in forge/settings.py.

Expects the argon2 python library to be installed. You should probably install bcrypt as well.

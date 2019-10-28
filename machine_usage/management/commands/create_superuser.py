from django.core.management.base import BaseCommand, CommandError
from machine_usage.models import User, UserProfile
from django.contrib.auth import get_user_model
from datetime import datetime

class Command(BaseCommand):
	help = 'Adds a superuser'

	def handle(self, *args, **options):
		get_user_model().objects.create_user(username="admin", email="forge_dev_admin@rish.dev", password="password", is_staff=True, is_superuser=True, last_login=datetime.now())

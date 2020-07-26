from django.core.management.base import BaseCommand, CommandError
from machine_usage.models import User, Machine, UserProfile, Usage, Resource, MachineType, MachineSlot, SlotUsage
from django.contrib.auth import get_user_model
from datetime import datetime

from dateutil import parser
from decimal import Decimal

import uuid

class Command(BaseCommand):
	help = 'Imports data from the old forge database format into the application.'

	def add_arguments(self, parser):
		parser.add_argument("user_file")
		parser.add_argument("project_file")

	def handle(self, *args, **options):
		print(f'User File: {options["user_file"]}\nProject File: {options["project_file"]}\n\nThis script will OVERWRITE YOUR DATABASE!\n\nPress Enter to continue..')
		input()

		User.objects.all().delete()
		Usage.objects.all().delete()

		user_file = open(options["user_file"], "r")
		project_file = open(options["project_file"], "r")

		user_lines = user_file.read().split("\n")
		project_lines = project_file.read().split("\n")

		user_file.close()
		project_file.close()

		user_lines = user_lines[1:]
		project_lines = project_lines[1:]

		users = []
		projects = []

		for line in user_lines:
			users.append(line.split("\t"))

		for line in project_lines:
			projects.append(line.split("\t"))

		for user in users:
			if not len(user) == 7:
				break

			rcs = user[0]
			rin = user[1]
			fname = user[2]
			lname = user[3]
			email = user[4]
			gender = user[5]
			major = user[6]

			gender = gender.lower()

			if gender not in ["male", "female", "other", "prefer_not_to_say"]:
				gender = "prefer_not_to_say"

			get_user_model().objects.create_user(first_name=fname, last_name=lname, username=rcs, email=email, password=str(uuid.uuid4()), is_staff=False, is_superuser=False, last_login=datetime.now())
			prof = User.objects.get(username=rcs).userprofile
			prof.gender = gender
			prof.major = major
			prof.rin = int(rin)
			prof.save()

		for project in projects:
			#print(f"Creating project {project}")
			if not len(project) == 11:
				break

			plastic = project[1]
			amount = project[2]
			machine_name = project[3]

			try:
				for_class = bool(int(project[4]))
			except:
				for_class = False

			start_time = parser.parse(project[5])

			try:
				eta_time = parser.parse(project[6])
			except:
				eta_time = None

			try:
				end_time = parser.parse(project[7])
			except:
				end_time = None

			try:
				successful = bool(int(project[8]))
			except:
				successful = False
			if not successful:
				print("Failed print parsed!")
				
			fail_count = int(project[9])
			rin = project[10]

			#print(f"Machine: {machine_name}")
			machine = Machine.objects.get(machine_name=machine_name)
			slots = machine.machine_type.machineslot_set.all()
			user_profile = UserProfile.objects.get(rin=int(rin))

			usage = Usage()

			usage.for_class = for_class
			usage.failed = not successful
			usage.is_reprint = (fail_count > 0)
			usage.userprofile = user_profile
			usage.machine = machine

			usage.complete = True

			usage.start_time = start_time
			usage.end_time = end_time
			usage.clear_time = end_time

			resource = Resource.objects.get(resource_name=plastic)

			try:
				amount_per_slot = float(amount) / float(len(slots))
			except:
				amount_per_slot = 0

			usage.save()
			usage.start_time = start_time
			usage.save()

			slot_usages = []

			for slot in slots:
				slot_usage = SlotUsage()
				slot_usage.machine_slot = slot
				slot_usage.usage = usage 
				slot_usage.resource = resource
				slot_usage.amount = Decimal(amount_per_slot)

				slot_usages.append(slot_usage)

			usage.save()

			for slot_usage in slot_usages:
				slot_usage.save()
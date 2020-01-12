from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from decimal import Decimal

import machine_usage.utils
import machine_usage.lists

import uuid

from datetime import datetime, timedelta

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	rin = models.PositiveIntegerField(default=None, null=True, blank=True, unique=True)
	gender = models.CharField(max_length=255, default="", blank=True, choices=machine_usage.lists.gender)
	major = models.CharField(max_length=255, default="", blank=True, choices=machine_usage.lists.major)

	email_verification_token = models.CharField(max_length=255, default="", blank=True, unique=True)

	def calculate_balance(self):
		balance = Decimal(15.00) # TODO: Make the cost per semester a constant somewhere.
		for usage in self.usage_set.all():
			balance += usage.cost()
		return balance

	def __str__(self):
		return f"{self.user.username} ({self.rin})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        email_verification_token = str(uuid.uuid4())
        UserProfile.objects.create(user=instance, email_verification_token=email_verification_token)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class Resource(models.Model):
	resource_name = models.CharField(max_length=255, unique=True)
	unit = models.CharField(max_length=255)
	cost_per = models.DecimalField(max_digits=5, decimal_places=2)

	in_stock = models.BooleanField(default=True)
	deleted = models.BooleanField(default=False)

	def __str__(self):
		return self.resource_name

class MachineType(models.Model):
	machine_type_name = models.CharField(max_length=255, unique=True)
	machine_category = models.CharField(max_length=255, null=True)

	hourly_cost = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

	data_entry_after_use = models.BooleanField(default=False) # Allow a user to check a machine out, marking it as used, and then enter usage info afterwards. Ex: Laser Cutter

	deleted = models.BooleanField(default=False)

	def __str__(self):
		return self.machine_type_name

	def get_slot(self, name):
		return self.machineslot_set.get(slot_name=name)

	def get_slot_names(self):
		out = []
		for element in self.machineslot_set.all():
			out.append(element.slot_name)
		return out

class MachineSlot(models.Model):
	slot_name = models.CharField(max_length=255)

	machine_type = models.ForeignKey(
		MachineType,
		on_delete = models.CASCADE
	)

	allowed_resources = models.ManyToManyField(Resource)
	deleted = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.machine_type.machine_type_name}'s {self.slot_name} slot"

	def resource_allowed(self, name):
		return True

class Machine(models.Model): # TODO make sure names of all slots added to machine are unique in scope
	machine_name = models.CharField(max_length=255, unique=True)
	machine_type = models.ForeignKey(
		MachineType,
		on_delete = models.CASCADE
	)

	in_use = models.BooleanField(default=False)
	current_job = models.OneToOneField(
		"Usage",
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name="current_machine" # Can we make this None? You can already see a usage's machine from usage.machine.
	)
	enabled = models.BooleanField(default=True)
	status_message = models.CharField(max_length=255, default="", blank=True)
	deleted = models.BooleanField(default=False)

	def __str__(self):
		return self.machine_name

class Usage(models.Model):
	machine = models.ForeignKey(
		Machine,
		on_delete = models.CASCADE
	)

	userprofile = models.ForeignKey(
		UserProfile,
		on_delete = models.CASCADE
	)

	for_class = models.BooleanField(default=False)
	
	start_time = models.DateTimeField(auto_now_add=True)
	end_time = models.DateTimeField(null=True, blank=True) # null/blank allowed for check-in/check-out machines

	retry_count = models.PositiveIntegerField(default=0)

	complete = models.BooleanField(default=False)
	deleted = models.BooleanField(default=False)

	def cost(self):
		cost = Decimal(0.00)
		for slot in self.slotusage_set.all():
			cost += Decimal(slot.cost())
		return cost

	def set_end_time(self, hours, minutes):
		self.end_time = self.start_time + timedelta(hours=hours, minutes=minutes)

	def __str__(self):
		return f"Usage of {self.machine} by {self.userprofile.user.username} at {self.start_time}"


class SlotUsage(models.Model):
	usage = models.ForeignKey(
		Usage,
		on_delete = models.CASCADE
	)

	machine_slot = models.ForeignKey(
		MachineSlot,
		on_delete = models.CASCADE
	)

	resource = models.ForeignKey(
		Resource,
		on_delete = models.CASCADE
	)

	amount = models.DecimalField(max_digits=10, decimal_places=5)
	deleted = models.BooleanField(default=False)

	def __str__(self):
		return f"Usage of {self.usage.machine}'s {self.machine_slot} by {self.usage.userprofile.user.username}"

	def cost(self):
		return self.amount * self.resource.cost_per

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from decimal import Decimal

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	rin = models.PositiveIntegerField(default=0, blank=True)
	gender = models.CharField(max_length=255, default="", blank=True)
	major = models.CharField(max_length=255, default="", blank=True)

	verified_email = models.BooleanField(default=False, blank=True)

	# TODO replace email verification with a group membership

	def calculate_balance(self):
		balance = Decimal(15.00) # TODO: Make this a constant somewhere.
		for usage in self.usage_set.all():
			balance += usage.cost()
		return balance

	def __str__(self):
		return f"{self.user.username} ({self.rin})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class Resource(models.Model):
	resource_name = models.CharField(max_length=255)
	unit = models.CharField(max_length=255)
	cost_per = models.DecimalField(max_digits=5, decimal_places=2)

	in_stock = models.BooleanField(default=True)
	deleted = models.BooleanField(default=False)

	def __str__(self):
		return self.resource_name

class MachineType(models.Model):
	machine_type_name = models.CharField(max_length=255)
	machine_category = models.CharField(max_length=255, null=True)

	deleted = models.BooleanField(default=False)

	def __str__(self):
		return self.machine_type_name

class MachineSlot(models.Model):
	slot_name = models.CharField(max_length=255)

	machine_type = models.ForeignKey(
		MachineType,
		on_delete = models.CASCADE
	)

	allowed_resources = models.ManyToManyField(Resource)

	deleted = models.BooleanField(default=False)

	def __str__(self):
		return self.slot_name

class Machine(models.Model):
	machine_name = models.CharField(max_length=255)
	machine_type = models.ForeignKey(
		MachineType,
		on_delete = models.CASCADE
	)

	in_use = models.BooleanField(default=False)
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

	for_class = models.BooleanField()
	
	start_time = models.DateTimeField(auto_now=True)
	planned_duration = models.DurationField()

	fail_time = models.DateTimeField(null=True)
	retry_count = models.PositiveIntegerField(default=0)

	complete = models.BooleanField()
	deleted = models.BooleanField(default=False)

	def cost(self):
		cost = Decimal(0.00)
		for slot in self.slotusage_set.all():
			cost += Decimal(slot.cost())
		return cost

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
		return f"Usage of {self.usage.machine}'s {self.machine_slot} slot by {self.usage.userprofile.user.username}"

	def cost(self):
		return self.amount * self.resource.cost_per

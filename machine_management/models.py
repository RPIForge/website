#django imports
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

#model imports
from user_management.models import *
from data_management.models import *
from business.models import *

#general imports
from decimal import Decimal
import uuid
from datetime import datetime, timedelta

#resource model
class Resource(models.Model):
    # ? Use: Keeps data on the resources that the forge uses
    # ! Data: Tracks name, unit type, and cost per unit

    resource_name = models.CharField(max_length=255, unique=True)
    unit = models.CharField(max_length=255)
    cost_per = models.DecimalField(max_digits=5, decimal_places=2)

    in_stock = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.resource_name

    def units_used(self):
        used = 0

        for slotusage in self.slotusage_set.all():
            used += slotusage.amount

        return used

class MachineType(models.Model):
    # ? Use: Keeps track of the different types of machines
    # ! Data: Tracks name, categroy, usage policy, usage cost


    machine_type_name = models.CharField(max_length=255, unique=True)
    machine_category = models.CharField(max_length=255, null=True)

    usage_policy = models.CharField(max_length=4096, default="")

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
    # ? Use: Keeps track of the individual machine slot
    # ! Data: Tracks the machine type its on, allowed resources

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

class Machine(models.Model): 
    # ? Use: Keeps track of the indivual machines
    # ! Data: Tracks name, current usage and job informatiom, and current pritner status


    machine_name = models.CharField(max_length=255, unique=True)
    machine_type = models.ForeignKey(
        MachineType,
        on_delete = models.CASCADE
    )

    in_use = models.BooleanField(default=False)
    
    current_print_information = models.ForeignKey(
        JobInformation,
        on_delete = models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_job"
    )
    
    current_job = models.OneToOneField(
        "Usage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_usage" # Can we make this None? You can already see a usage's machine from usage.machine.
    )
    
    
    
    enabled = models.BooleanField(default=True)
    status_message = models.CharField(max_length=255, default="", blank=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.machine_name

    def time_used(self):
        #print(self.machine_name)
        elapsed_time = timedelta(hours=0, minutes=0)

        for usage in self.usage_set.all():
            #print(usage.elapsed_time())
            elapsed_time += usage.elapsed_time()

        #print(elapsed_time)
        if (elapsed_time.days > 0):
            return f"{elapsed_time.days}d {elapsed_time.seconds // 3600}h {int(elapsed_time.seconds // 60 % 60.0)}m"
        else:
            return f"{elapsed_time.seconds // 3600}h {int(elapsed_time.seconds // 60 % 60.0)}m"
    
    
    

class Usage(models.Model):
    # ? Use: Keeps track of each usage in the forge
    # ! Data: Tracks usage cost, machien used, usage status

    machine = models.ForeignKey(
        Machine,
        on_delete = models.SET_NULL,
        null=True
    )
    
    current_print_information = models.ForeignKey(
        JobInformation,
        on_delete = models.SET_NULL,
        null=True,
        related_name="job"
    )
    
    userprofile = models.ForeignKey(
        UserProfile,
        on_delete = models.SET_NULL,
        null=True
    )

    semester = models.ForeignKey(
        Semester,
        on_delete=models.SET_NULL,
        null=True
    )
    
    
    
    
    for_class = models.BooleanField(default=False)
    is_reprint = models.BooleanField(default=False)
    own_material = models.BooleanField(default=False)

    cost_override = models.BooleanField(default=False)
    overridden_cost = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cost_override_reason = models.CharField(max_length=512, default="", blank=True)
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True) # null/blank allowed for check-in/check-out machines

    clear_time = models.DateTimeField(null=True, blank=True)

    retry_count = models.PositiveIntegerField(default=0)

    status_message = models.CharField(max_length=255, default="In Progress.", blank=False)

    complete = models.BooleanField(default=False)
    error = models.BooleanField(default=False)
    failed = models.BooleanField(default=False)
    
    deleted = models.BooleanField(default=False)
    
    def cost(self):
        cost = Decimal(0.00)

        if self.cost_override:
            return self.overridden_cost

        if self.own_material:
            return cost

        if self.is_reprint:
            return cost

        for slot in self.slotusage_set.all():
            cost += Decimal(slot.cost())

        if self.end_time is not None:
            usage_time = (self.end_time - self.start_time).total_seconds()
        else:
            usage_time = 0

        cost += Decimal(self.machine.machine_type.hourly_cost / (60 * 60)) * Decimal(usage_time)

        return cost

    def set_end_time(self, hours, minutes):
        self.end_time = self.start_time + timedelta(hours=hours, minutes=minutes)

    def elapsed_time(self):
        if self.failed:
            return (self.clear_time - self.start_time)
        elif (self.end_time is not None) and (self.complete or (self.end_time < timezone.now())): # Validate this
            return (self.end_time - self.start_time)
        else:
            return (timezone.now() - self.start_time)

    def __str__(self):
        return f"Usage of {self.machine} by {self.userprofile.user.username} at {self.start_time} during {self.semester}"


class SlotUsage(models.Model):
    # ? Use:Keeps track how much each slot was used
    # ! Data: Tracks slot, resource, ammount

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


        
        
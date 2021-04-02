#django imports
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_date


#model imports
from user_management.models import *
from machine_management.models import *
from business.models import *

#general imports
from datetime import datetime

class JobInformation(models.Model): 
    # ? Use: Keeps track of all general information received from a printer. 
    # ! Data: Tacks job start and end, current status message, and file id

    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True) # null/blank allowed for check-in/check-out machines

    status_message = models.CharField(max_length=255, default="In Progress.", blank=False)

    complete = models.BooleanField(default=False)
    error = models.BooleanField(default=False)

    file_id = models.CharField(max_length=36, null=True, blank=True, default=None)
    layer_count = models.IntegerField(null=True, blank=True)

        
    usage = models.ForeignKey(
        "machine_management.Usage",
        on_delete = models.SET_NULL,
        null=True,
        blank=True
    )

    machine = models.ForeignKey(
        "machine_management.Machine",
        on_delete = models.CASCADE,
        null=False,
    )
    

    def __str__(self):
        return "Job on {} starting at {}".format(self.machine.machine_name, self.start_time)

    def percentage(self):
        if(not self.end_time):
            return 0
        duration = self.end_time - self.start_time
        elapsed = timezone.now() - self.start_time
        percentage = (elapsed.total_seconds() / duration.total_seconds()) * 100
        if(percentage > 100):
            percentage = 100
        return percentage
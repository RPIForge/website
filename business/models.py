from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from decimal import Decimal
import uuid

from datetime import datetime, timedelta

class Semester(models.Model):
    # ? Use: Keeps track of the semester objects
    # ! Data: Tracks year, season, and if its the most recent
    
    year = models.IntegerField(blank=False)
    season = models.CharField(max_length=255,blank=False)
    current = models.BooleanField(default=True)
    
    # message used for machine usaage policy
    buisness_message = models.TextField(default="")

    def get_usages(self):
        return self.usage_set.all().select_related('organization')\
            .prefetch_related('slotusage_set__machine_slot').prefetch_related('slotusage_set__resource')

    def __str__(self):
        if(self.current):
            return f"{self.season} {self.year} (current semester)"
        else:
            return f"{self.season} {self.year}"
    
    
    def save(self, *args, **kwargs):
        if self.current:
            semesters = Semester.objects.all().filter(current=True)
            for years in semesters:
                years.current = False
                years.save()
            
        super(Semester, self).save(*args, **kwargs)
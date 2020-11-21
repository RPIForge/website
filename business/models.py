from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from decimal import Decimal

from user_management.models import UserProfile

import uuid

from datetime import datetime, timedelta

class Semester(models.Model):
    year = models.IntegerField(blank=False)
    season = models.CharField(max_length=255,blank=False)
    current = models.BooleanField(default=True)
    
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

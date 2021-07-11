from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from decimal import Decimal

import user_management.lists

import uuid

from datetime import datetime, timedelta

class UserProfile(models.Model):
    # ? Use: Keeps track of extra user profile information
    # ! Data: Rin,gender,major, graduating, uuid

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rin = models.PositiveIntegerField(default=None, unique=True)
    gender = models.CharField(max_length=255, default="", blank=True, choices=user_management.lists.gender)
    major = models.CharField(max_length=255, default="", blank=True, choices=user_management.lists.major)

    is_active = models.BooleanField(default=False)
    is_graduating = models.BooleanField(default=False)
    anonymous_usages = models.BooleanField(default=False)

    email_verification_token = models.CharField(max_length=255, default="", blank=True, unique=True)

    entertainment_mode = models.BooleanField(default=False)
    
    uuid = models.UUIDField(default = uuid.uuid4, editable = False) 
    
    def calculate_balance(self):
        if(not self.user.groups.filter(name = "member").exists()):
            return Decimal(0.00)
            
        balance = Decimal(15.00) # TODO: Make the cost per semester a constant somewhere.
        for usage in self.usage_set.all():
            if(usage.semester.current):
                balance += usage.cost()
                
        return balance

    def __str__(self):
        return f"{self.user.username} ({self.rin})"
    
    class Meta:
        db_table = 'user_management_userprofile'

# ! Function: Create userprofile from User creation
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not kwargs.get('raw', False): # `and not ...` included to allow fixture imports.
        email_verification_token = str(uuid.uuid4())
        new_uuid = str(uuid.uuid4())
        UserProfile.objects.create(user=instance, email_verification_token=email_verification_token, uuid=new_uuid)

# ! Function: Save the user profile
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

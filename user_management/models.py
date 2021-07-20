from django.db import models
from django.apps import apps
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from decimal import Decimal

import user_management.lists

import uuid

from datetime import datetime, timedelta

class UserProfile(models.Model):
    # ? Use: Keeps track of extra user profile information
    # ! Data: Rin,gender,major, graduating, uuid

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # ? uniqueness for rin is checked in save due to allowing multiple null values

    rin = models.PositiveIntegerField(default=None, null=True, blank=True)
    gender = models.CharField(max_length=255, default="", blank=True, choices=user_management.lists.gender)
    major = models.CharField(max_length=255, default="", blank=True, choices=user_management.lists.major)

    is_active = models.BooleanField(default=False)
    is_graduating = models.BooleanField(default=False)
    anonymous_usages = models.BooleanField(default=False)

    email_verification_token = models.CharField(max_length=255, default="", blank=True, unique=True)

    entertainment_mode = models.BooleanField(default=False)
    
    uuid = models.UUIDField(default = uuid.uuid4, editable = False) 
    
    def get_organizations(self):
        output = set()
        for membership in self.user.memberships.all().select_related('organization'):
            output.add(membership.organization)
        return output

    def get_organization_fees(self):
        output = float()
        for org in self.get_organizations():
            output += float(org.membership_fee)
        return output
        
    def get_accessable_machines(self):
        orgs = self.get_organizations()
        machine_list = set()
        for org in orgs:
            machine_list = machine_list.union(org.get_accessable_machines())
        return machine_list


    def get_usages(self):
        Usage = apps.get_model('machine_management.Usage')
        return Usage.all().filter(userprofile=self)

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
    
 
    def save(self, *args, **kwargs):
        if(self.rin is not None):
            object_list = UserProfile.objects.all().filter(rin=self.rin)
            for obj in object_list:
                if(obj!=self):
                    raise ValidationError()
        super(UserProfile, self).save(*args, **kwargs)

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

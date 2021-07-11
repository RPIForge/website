#django imports
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import (
    check_password, is_password_usable, make_password,
)
from django.utils.translation import gettext_lazy as _

#model imports

#general imports
import uuid

class Organization(models.Model): 
    # ? Use: Keeps Track of an Organization
    # ! Data: 


    # identifier
    org_id = models.CharField(max_length=6, editable=False, blank=False)

    #general information
    name = models.CharField(max_length=255, unique=True, blank=False)
    description = models.CharField(max_length=255, default='')

    #used to identifiy the primary org. This should be the forge
    default = models.BooleanField(default=False)

    #password to join organization
    # ? this was stolon from https://github.com/django/django/blob/ca9872905559026af82000e46cde6f7dedc897b6/django/contrib/auth/base_user.py
    password = models.CharField(_('password'), max_length=128)


    #how much we charge the organization to use our site/forge resources
    organization_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    #cost for a user to join the organization
    membership_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    # bill membe
    bill_member = models.BooleanField(default=True)

    # if organization can be joined by the public
    public = models.BooleanField(default=False)
    
    # IF an organization can be seen in the org list
    visible = models.BooleanField(default=False)

    def get_membership(self, user):
        return OrganizationMembership.objects.filter(user=user,organization=self).first()

    def add_user(self, user):
        membership = self.get_membership(user)
        if(not membership):
            membership = OrganizationMembership()
            membership.organization = self
            membership.user = user
            membership.save()

        return membership
    
    def remove_user(self,user):
        OrganizationMembership.objects.filter(user=user,organization=self).delete()
    
    def save(self, *args, **kwargs):
        self.org_id =  str(uuid.uuid4())[:6]

        if self.default:
            orgs = Organization.objects.all().filter(default=True)
            for org in orgs:
                org.default = False
                org.save()

        super(Organization, self).save(*args, **kwargs)

    def __str__(self):
        return "{}".format(self.name)




class OrganizationMembership(models.Model): 
    # ? Use: Keeps Track of an OrganizationMembership
    # ! Data:  Organization, user and if they're a manager


    #general information
    organization = models.ForeignKey(
        Organization,
        on_delete = models.CASCADE,
        default = 1,
        null=False,
        blank=False,
        related_name="memberships"
    )

    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        default = 1,
        null=False,
        blank=False,
        related_name="machines"
    )

    #used to identify is a user is a manager of an org
    manager = models.BooleanField(default=False)

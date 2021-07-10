#django imports
from django.db import models
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

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        # Set a value that will never be a valid hash
        self.password = make_password(None)


    def verify_user(self, password):
        return self.check_password(password)
       
    def save(self, *args, **kwargs):
        self.org_id =  str(uuid.uuid4())[:6]

        if self.default:
            orgs = Organization.objects.all().filter(default=True)
            for org in orgs:
                org.default = False
                org.save()

        super(Organization, self).save(*args, **kwargs)

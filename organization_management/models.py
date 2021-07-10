#django imports
from django.db import models

#model imports

#general imports
import uuid

class Organization(models.AbstractBaseUser): 
    # ? Use: Keeps Track of an Organization
    # ! Data: 

    # identifier
    org_id = models.CharField(max_length=6, editable=False, blank=False)

    #general information
    name = models.CharField(max_length=255, unique=True, blank=False)
    description = models.CharField(max_length=255, default='')

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


    USERNAME_FIELD = "name"

    def verify_user(self, password):
        return self.check_password(password)
       
    def save(self, *args, **kwargs):
        self.org_id =  str(uuid.uuid4())[:6]
        super(Organization, self).save(*args, **kwargs)

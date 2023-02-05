#django imports
from django.db import models
from django.core.validators import MinValueValidator
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
from itertools import chain
import abc

#resource model
class ResourceCategory(models.Model):
    # ? Use: Keeps data on the types resources that the forge uses. i.e. pla/petg filament
    # ! Data: Tracks name, unit type, and cost per unit

    resource_name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, default="",null=True, blank=True)
    unit = models.CharField(max_length=255,default="", blank=True)
    cost_per = models.DecimalField(max_digits=5, decimal_places=2,blank=True,null=True)

    deleted = models.BooleanField(default=False)

    @property
    def resources(self):
        # This is expensive
        return chain(self.quantityresource_set.all(),self.individualresource_set.all())

    @property
    def in_stock(self):
        for resource in self.resources:
            if resource.in_stock:
                return True
        return False

    def units_used(self):
        used = 0

        for slotusage in self.slotusage_set.all():
            used += slotusage.amount

        return used

    def __str__(self):
        return self.resource_name



class Resource(models.Model):
    # ? Use: Keeps track of generic resource information 
    # ! Data: Tracks category, cost_override, and common descriptors

    # General resource information
    resource_category = models.ForeignKey(ResourceCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=255, blank=True,default="n/a")
    description = models.CharField(max_length=255,blank=True,default="")
    cost_override = models.DecimalField(max_digits=5, decimal_places=2, blank=True,null=True, default=None)

    # brand or Manufacturer 
    brand = models.CharField(max_length=255, blank=True)

    # Descriptors like color, shape/size, and weight 
    color = models.CharField(max_length=255, blank=True)
    shape = models.CharField(max_length=255, blank=True)
    weight = models.CharField(max_length=255, blank=True)

    @abc.abstractproperty
    def in_stock(self):
        pass
    
    def __repr__(self):
        descriptors = [self.name,self.brand,self.color,self.shape]
        nonnull = [i for i in descriptors if i != ""]
        return '/'.join(nonnull)

    def __str__(self):
        return f"{self.resource_category}/{self.__repr__()}"

    class Meta:
        abstract = True

class ResourceCondition(models.Model):
    # ? User: Keep track of individual resource conditions
    # ! Data: Tracks condition name
    condition = models.CharField(max_length=255)
    usable = models.BooleanField(default=True)

    def in_stock(self):
        return self.usable

    def __str__(self):
        return f"{self.condition}"

class QuantityResource(Resource):
    quantity = models.BigIntegerField()
    def in_stock(self):
        return self.quantity > 0

    def __str__(self):
        return f"{super().__str__()}/{self.quantity}"

class IndividualResource(Resource):
    resource_condition = models.ForeignKey(ResourceCondition, on_delete=models.PROTECT)
    def __str__(self):
        return f"{super().__str__()}/{self.id}/{self.resource_condition.condition}"
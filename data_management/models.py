#django imports
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.dateparse import parse_date

from influxdb_client import Point
from forge.settings import INFLUX_ORG, influx_write

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

class RecurringData(models.Model):
    time = models.DateTimeField(editable= False)
    
    job = models.ForeignKey(
        JobInformation,
        on_delete = models.SET_NULL,
        null=True,
        blank = True,
        editable= False
    )

    machine = models.ForeignKey(
        "machine_management.Machine",
        on_delete = models.CASCADE,
        null=False,
        editable = False
    )

    #def generic get_bucket
    def get_bucket(self):
        raise ValueError("RecurringData must implement get_bucket")

    def save(self, *args, **kwargs):
        if(self.time is None):
            self.time = datetime.now()
        
        if(isinstance(self.time,str)):
            self.time = datetime.strptime(self.time, "%Y-%m-%d %H:%M:%S")

        self.time = make_aware(self.time)
            

        self.clean()

        bucket = self.get_bucket()

        data_point = Point(str(self))
        for field in self._meta.get_fields():
            #get object name amd skip name field
            name = field.name
            
            #get object value
            field_object = self._meta.get_field(field.name)
            value = field_object.value_from_object(self)

            

            #handle custom points
            if(name is "time"):
                data_point.time(value)

            elif(name is "machine"):
                #TODO Fix this. This should be able to be imported above
                from machine_management.models import Machine


                machine = Machine.objects.get(id=value)
                data_point.tag("machine_name", machine.machine_name)
                data_point.tag("machine_type", machine.machine_type.machine_type_name)
                data_point.tag("machine_id", machine.id)

            elif(name is "job" and value is not None):
                job = JobInformation.objects.get(id=value)
                data_point.tag("job", str(job))
                data_point.tag("job_id", job.id)

            elif(name is 'name'):
                data_point.tag("name",value)

            elif(value is not None):
                data_point.field(name,float(value))
                
        influx_write.write(bucket,INFLUX_ORG, data_point)
   
    class Meta:
        #this is for inheritance
        abstract = True

        #This allows for influxDb
        managed = False

class ToolTemperature(RecurringData): 
    # ? Use: Keeps track of temperature at a point in time
    # ! Data: Temperature in Celcius
    name = models.CharField(max_length=255, editable = False)
    temperature = models.FloatField(editable = False)
    temperature_goal = models.FloatField(editable = False)

    def get_bucket(self):
        return 'temperature_data'

    def __str__(self):
        return "{}'s {} temperature data at {}".format(self.machine.machine_name, self.name, self.time)  

    class Meta:

        #This allows for influxDb
        managed = False

class LocationInformation(RecurringData): 
    # ? Use: Keeps track of temperature at a point in time
    # ! Data: Temperature in Celcius
    layer = models.IntegerField(editable = False)
    max_layer = models.IntegerField(editable = False)

    z_location = models.FloatField(editable = False)

    def get_bucket(self):
        return 'location_data'

    def __str__(self):
        return "{} location data at {}".format(self.machine.machine_name, self.time)  

    class Meta:

        #This allows for influxDb
        managed = False

        
        
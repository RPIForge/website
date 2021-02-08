#django imports
from django import forms
from django.db.models.base import ObjectDoesNotExist 
from django.utils import timezone

#local imports
from influxdb_client import Point
from forge.settings import INFLUX_ORG, influx_write

#model import
from machine_management.models import *
from data_management.models import *


class RecurringData():
    # ? Use: Generic form to validate recurring data
    # ! Fields: time, job, and machine

    '''
    This model is used for generic time series data. It will implement accessors and mutators for influxdb. 
    The data stored in this influxdb will be short term access as data will be deleted every couple of days
    automatically. This is just to access data for our users. The long term storage will be done elsewhere.
    '''

    time = None
    job = None
    machine = None

    fields = []
    

    #
    # accessors required by Inheritance
    #

    #generic get_bucket
    def get_bucket(self):
        raise ValueError("RecurringData must implement get_bucket")

    #generic  get_name
    def get_name(self):
        raise ValueError("RecurringData must implement get_name")
    
    #
    # Helper function
    #
    def get_time(self):
        time = self.time
        if(self.time is None):
            time = timezone.now()

        if(isinstance(self.time,str)):
            time = datetime.strptime(self.time, "%Y-%m-%d %H:%M:%S %Z")

        if(self.time.tzinfo is not None):
            time = make_aware(self.time)

        return time

    #submit data to the InfluxDB
    def submit_data(self):
        self.time = self.get_time()            
         
        if(self.machine is None):
            raise ValueError("Machine must not be None")
        

        bucket = self.get_bucket()

        data_point = Point(self.get_name())
    
        #handle custom points
        data_point.time(self.time.isoformat())
        data_point.tag("machine_name", self.machine.machine_name)
        data_point.tag("machine_type", self.machine.machine_type.machine_type_name)
        data_point.tag("machine_id", self.machine.id)
        if(self.job is not None):
            data_point.tag("job", str(self.job))
            data_point.tag("job_id", self.job.id)
            
        for field in self.fields:
            #get object value
            value = getattr(self, field)

            if(isinstance(value, str)):
                data_point.tag(field,str(value))

            elif(value is not None):
                data_point.field(field,float(value))

        try: 
            influx_write.write(bucket,INFLUX_ORG, data_point)
        except:
            print("Unable to write to {}".format(self.get_bucket()))
            

class TemperatureInformation(RecurringData): 
    # ? Use: Keeps track of temperature at a point in time
    # ! Data: Temperature in Celcius
    name = None
    temperature = None
    temperature_goal = None

    fields = RecurringData.fields + ['name', 'temperature', 'temperature_goal']

    def get_bucket(self):
        return 'temperature_data'

    def get_name(self):
        return "{}'s {} temperature".format(self.machine.machine_name, self.name)

class LocationInformation(RecurringData): 
    # ? Use: Keeps track of location at a point in time
    # ! Data: Location in either layer count or z location
    layer = None
    max_layer = None

    height = None
    max_height = None

    fields = RecurringData.fields + ['layer', 'max_layer', 'height','max_height']

    def get_bucket(self):
        return 'location_data'

    def get_name(self):
        return "{}'s location".format(self.machine.machine_name)

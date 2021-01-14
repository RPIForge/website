#django imports
from django import forms
from django.db.models.base import ObjectDoesNotExist 

#local imports
from influxdb_client import Point
from forge.settings import INFLUX_ORG, influx_write

#model import
from machine_management.models import *
from data_management.models import *


class RecurringData():
    # ? Use: Generic form to validate recurring data
    # ! Fields: time, job, and machine
    time = None
    job = None
    machine = None

    fields = []

    #generic get_bucket
    def get_bucket(self):
        raise ValueError("RecurringData must implement get_bucket")

    #data name
    def get_name(self):
        raise ValueError("RecurringData must implement get_name")

    #submit data to the InfluxDB
    def submit_data(self):
        if(self.time is None):
            self.time = datetime.now()
        
        if(isinstance(self.time,str)):
            self.time = datetime.strptime(self.time, "%Y-%m-%d %H:%M:%S")

        if(self.time.tzinfo is not None):
            self.time = make_aware(self.time)
            
         
        if(self.machine is None):
            raise ValueError("Machine must not be None")
        

        
        bucket = self.get_bucket()

        data_point = Point(self.get_name())
    
        #handle custom points
        data_point.time(self.time)
        data_point.tag("machine_name", self.machine.machine_name)
        data_point.tag("machine_type", self.machine.machine_type.machine_type_name)
        data_point.tag("machine_id", self.machine.id)
        if(self.job is not None):
            data_point.tag("job", str(self.job))
            data_point.tag("job_id", self.job.id)

        for field in self.fields:
            #get object value
            value = getattr(self, field)

            if(field == 'name'):
                data_point.tag("name",value)

            elif(value is not None):
                data_point.field(field,float(value))

        print(data_point)   
        influx_write.write(bucket,INFLUX_ORG, data_point)
            

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
        return "{}'s {}".format(self.machine.machine_name, self.name)

class LocationInformation(RecurringData): 
    # ? Use: Keeps track of temperature at a point in time
    # ! Data: Temperature in Celcius
    layer = forms.IntegerField()
    max_layer = forms.IntegerField()

    z_location = forms.FloatField()

    def get_bucket(self):
        return 'location_data'

    def get_name(self):
        return "location"

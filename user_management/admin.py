from django.contrib import admin
from django.urls import reverse

from user_management.models import *
from user_management.forms import *
from machine_management.models import *
from django.contrib.auth.models import User, Group

from django.contrib import admin

from django import forms
from django.utils.safestring import SafeText



class ForgePrintAdmin(admin.ModelAdmin):
    
    #fields =('get_temperature',)
    
    
    readonly_fields=('get_temperature',)
    
    
    def get_temperature(self, object):
        return "<iframe src='/api/machines/print/temperature?job_id={}&display_graph=1' /></iframe>".format(object.id)
        
    get_temperature.allow_tags = True 
    get_temperature.short_description = "Temperature Information"

        

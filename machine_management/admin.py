from django.contrib import admin
from django.urls import reverse

from user_management.models import *
from user_management.forms import *
from machine_management.models import *
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin

from django import forms
from django.utils.safestring import SafeText

class JobInformationAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'size':'20'})},
        models.TextField: {'widget': forms.Textarea(attrs={'rows':4, 'cols':40})},
    }


    # ? Use: Add search fields to user profile admin
    fieldsets = [
        
        (None, {
            'fields': ('end_time', 'status_message', 'complete', 'error', 'file_id', 'usage', 'machine')
        }),
        ('Printer Information', {
            'fields': ('get_graph',)
        }),
    
    ]

    readonly_fields=('get_graph',)

    def get_graph(self, object):
        iframe_text = "<iframe class='temperature' size='10' src='/api/machines/print/temperature?job_id={}&display_graph=1' style='min-height:450px; width:100%;' scrolling='yes'></iframe>".format(object.id)
        #iframe_text = "<a href='/api/machines/print/temperature?job_id={}&display_graph=1'>Temperature Information</a>".format(object.id)
        return SafeText(iframe_text)


    get_graph.allow_tags = True 
    get_graph.short_description = "Temperature Information"

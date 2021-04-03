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
    # ? Use: Add search fields to user profile admin
    fieldsets = [
        
        (None, {
            'fields': ('end_time', 'status_message', 'complete', 'error', 'file_id', 'usage', 'machine')
        }),
    
    ]



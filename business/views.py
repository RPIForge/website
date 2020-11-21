# Importing Django Utils
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings

# Importing Models
from django.contrib.auth.models import User, Group

from machine_management.models import *
from machine_management.forms import *


# Importing Other Libraries
import json
from datetime import datetime
from decimal import Decimal
from datetime import datetime, timedelta


@login_required
def render_change_semesters(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        semester_form = SemesterCreationForm(request.POST)
        # check whether it's valid:
        if semester_form.is_valid():
            # process the data in form.cleaned_data as required
            semester = semester_form.save()
            
            members = Group.objects.get(name='member') 
            volunteers = Group.objects.get(name='volunteers') 
            managers = Group.objects.get(name='managers') 
            admins = Group.objects.get(name='admins') 
            
            #clear members, volunteers, managers
            members.user_set.clear()
            volunteers.user_set.clear()
            managers.user_set.clear()
            
            for user in admins.user_set.all():
               user.groups.add(members, managers, volunteers)
                
                
            # redirect to a new URL:
            return render(request, 'myforge/forms/change_semester.html', {'submit': True}) 

    # if a GET (or any other method) we'll create a blank form
    else:
        semester_form = SemesterCreationForm()
        
    
    return render(request, 'myforge/forms/change_semester.html', {'semester_form': semester_form}) 
    
    

@login_required
def render_charge_sheet(request):
    semester = Semester.objects.all().order_by("-current")
    semester_list = []
    for item in semester:
        semester_list.append({'id': item.id, 'name': str(item)})
    
    return render(request, 'myforge/forms/charge_sheet.html', {'semester_list':semester_list})
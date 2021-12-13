# Importing Django Utils
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings

# Importing Models
from django.contrib.auth.models import User, Group
from business.models import Semester
from machine_management.models import *
from organization_management.models import *
from .forms import *


# Importing Other Libraries
import json
from datetime import datetime
from decimal import Decimal
from datetime import datetime, timedelta





# ! type: GET
# ! function: Generate table of all usages this semester
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
@login_required     
def list_semesters(request):
    context = {
        "table_headers":["Semester"],
        "table_rows":[],
        "page_title":"Semesters",
        "edit_root":"business/semester"
    }

    semesters = Semester.objects.all()
    for s in semesters:
        context["table_rows"].append({
            "row":[s],
            "id":s.id
        })

    return render(request, 'myforge/forms/list_items.html', context)

# ! type: GET/POST 
# ! function: Render page to create/end semester 
# ? required: None/Filled Form
# ? returns: HTTP Rendered Template
# TODO: 
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
            return render(request, 'business/change_semester.html', {'submit': True}) 

    # if a GET (or any other method) we'll create a blank form
    else:
        semester_form = SemesterCreationForm()
        
    
    return render(request, 'business/change_semester.html', {'semester_form': semester_form}) 
    
    
# ! type:GET
# ! function: Render page to download charge sheets 
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
@login_required
def render_charge_sheet(request):
    semesters = Semester.objects.all().order_by("-current")
    semester_list = []
    for semester in semesters:
        semester_list.append({'id':semester.id,'name':str(semester)})

    organizations = Organization.objects.all()
    organization_list = []
    for organization in organizations:
        organization_list.append({'id':organization.org_id,'name':organization.name})
    
    return render(request, 'business/charge_sheet.html', {'semester_list':semester_list, 'organization_list':organization_list})
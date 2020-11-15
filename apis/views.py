

# Importing Django Utils
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models.base import ObjectDoesNotExist
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings # import the settings file

#importing functions
from machine_usage.views import create_machine_usage
from forge import utils

# Importing Models
from machine_management.models import *
from django.contrib.auth.models import User, Group
from user_management.models import *


# Importing Other Libraries
import json
from decimal import Decimal
from datetime import datetime, timedelta
import csv

#
#   API
#

@csrf_exempt # TODO FIX THIS
@login_required
def clear_machine(request):
    if request.method == "POST":
        data = json.loads(request.body)

        if "machine_id" not in data:
            return HttpResponse("No machine_id provided.", status=400)

        machine = Machine.objects.get(id=int(data["machine_id"]))

        if not machine.in_use:
            return HttpResponse("Machine was not in use.", status=200)

        usage = machine.current_job
        usage.clear_time = timezone.now()
        usage.complete = True
        if (not usage.error) and (not usage.failed):
            usage.status_message = "Cleared."
        usage.save()

        machine.current_job = None
        machine.in_use = False
        machine.save()
        return HttpResponse("Machine cleared.", status=200)
    else:
        return HttpResponse("", status=405) # Method not allowed


@csrf_exempt # TODO FIX THSI
@login_required
def fail_machine(request):
    if request.method == "POST":
        data = json.loads(request.body)

        if "machine_id" not in data:
            return HttpResponse("No machine_id provided.", status=400)

        machine = Machine.objects.get(id=int(data["machine_id"]))

        if not machine.in_use:
            return HttpResponse("Machine was not in use.", status=200)

        usage = machine.current_job
        usage.clear_time = timezone.now()
        usage.failed = True
        usage.status_message = "Failed."
        usage.save()

        utils.send_failure_email(usage)
        return HttpResponse("Machine marked as failed.", status=200)
    else:
        return HttpResponse("", status=405) # Method not allowed

@csrf_exempt # TODO REMOVE THIS DECORATOR, ONLY FOR DEBUG
def machine_endpoint(request):
    if request.method == 'GET':
        output = []

        machines = Machine.objects.all().order_by("machine_name")

        for m in machines:
            if not m.deleted:
                machine_entry = {
                    "name": m.machine_name,
                    "in_use": m.in_use,
                    "enabled": m.enabled,
                    "status": m.status_message,
                    "usage_policy": m.machine_type.usage_policy,
                    "hourly_cost": float(m.machine_type.hourly_cost),
                    "slots": []
                }

                slots = m.machine_type.machineslot_set.all()
                for s in slots:
                    slot_entry = {
                        "slot_name": s.slot_name,
                        "allowed_resources": []
                    }

                    for r in s.allowed_resources.all():
                        if r.in_stock and not r.deleted:
                            slot_entry["allowed_resources"].append({"name":r.resource_name, "unit":r.unit, "cost":float(r.cost_per)})

                    machine_entry["slots"].append(slot_entry)

                output.append(machine_entry)

        return HttpResponse(json.dumps(output))
    elif request.method == 'POST':
        return create_machine_usage(request) # Make sure this still checks for login!
    else:
        return HttpResponse("", status=405) # Method not allowed
        
#
#Users
#
  
def verify_user(request):
    if request.method == 'GET':
        uuid = request.GET.get('uuid', '')
        try:
            userprofile = UserProfile.objects.get(uuid=uuid)
        except  UserProfile.DoesNotExist:
            return HttpResponse(status=204)
        except ValidationError:
            return HttpResponse(status=404)
        
        user = userprofile.user
        
        if(user.groups.filter(name="admins").exists()):
            return HttpResponse("admins")
        elif(user.groups.filter(name="managers").exists()):
            return HttpResponse("managers")
        elif(user.groups.filter(name="volunteers").exists()):
            return HttpResponse("volunteers")
        elif(user.groups.filter(name="member").exists()):
            return HttpResponse("member")
        else:
            return HttpResponse("user")
            

#
#Volunteers
#    
    
def current_volunteers(request):
    if request.method == 'GET':
        if(settings.CALENDAR == None):
            return HttpResponse(503)
        else:
            output = []
            events = settings.CALENDAR.get_current_events()
            for names in events:
                output.append(names['description'])
                
            
            return HttpResponse(json.dumps(output))
            
#
# Billing
#
#get charge sheet for the userss
def charge_sheet(request):
    if request.method == 'GET':
        graduating = request.GET.get('graduating', False)
        semester_id = request.GET.get('semester_id', None)
        
        if(not semester_id):
            return HttpResponse("No Semester Provided.", status=400) 
        
        semester = Semester.objects.get(id=semester_id)
        
        
        #get the list of users depneidng on if they are graduating
        #We charge memebrs differently if they are graduating or not.
        if(graduating):
            usages = semester.usage_set.filter(userprofile__is_graduating=True)
        else:
            usages = semester.usage_set.filter(userprofile__is_graduating=False)
        
        
        #if data reading has already been done update
        user_dict = {}
        if(semester.usage_summary):
            usages = usages.filter(start_time__lte=semester.usage_update)

            if(usages):
                output_dict = json.loads(semester.usage_summary)
                user_dict = output_dict['user_dict']
            else:
                print("return 1")
                return HttpResponse(semester.usage_summary)
              
            
        
        total_revenue = 0
        for usage in usages:
            name = usage.userprofile.user.get_full_name()
            cost = usage.cost()
            
            if(name in user_dict):
                user_dict[name]['balance'] = float(user_dict[name]['balance']) + float(cost)
            else:
                user_dict[name] = {'rin':usage.userprofile.rin, 'balance':float(cost+15)}
                
            total_revenue = float(total_revenue) + float(cost) + float(15)
            
        output = {'user_dict': user_dict, 'total_revenue': float(total_revenue)}
        
        output_string = json.dumps(output)
        
        semester.usage_summary = output_string
        semester.usage_update = datetime.now() 
        semester.save()
        
        print("return 2")
        return HttpResponse(output_string)
            
        
        
        

        
    


    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
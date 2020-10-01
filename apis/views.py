

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
from apis.models import *

# Importing Other Libraries
import json
from datetime import datetime
from decimal import Decimal
from datetime import datetime, timedelta

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
     


def verify_key(request):
    if("X-Api-Key" in request.headers):
        return Key.objects.filter(key=request.headers["X-Api-Key"]).exists()
    return False


#get or set machine status. machine id must be in data
#available statuses:
##completed: print ended
##printing: printing 
##error: printer errored out
@csrf_exempt
def machine_status(request):
    if(request.method == 'GET'):
        
        machine_id = request.GET.get("machine_id",None)
        
        if(not machine_id):
            return HttpResponse("No machine_id provided.", status=400)
        machine_id = int(machine_id)
        
        machine = Machine.objects.get(id=machine_id)
        if(machine.current_job != None):
            return HttpResponse(machine.current_job.status_message, status=200)
        else:
            return HttpResponse("Idle.", status=200)
        
    else:
        if(not verify_key(request)):
            return HttpResponse("Invalid or missing API Key", status=403)
        
        machine_id = request.GET.get("machine_id",None)
        if(not machine_id):
            return HttpResponse("No machine_id provided.", status=400)
        machine_id = int(machine_id)
        
        machine_status = request.GET.get("status",None)
        if(not machine_status):
            return HttpResponse("No status provided.", status=400)
            
        machine = Machine.objects.get(id=machine_id)
        usage = machine.current_job
        if(machine_status=="completed"):
            if(usage):
                usage.status_message = "Completed."
                usage.complete = True
                usage.end_time = timezone.now()
                usage.save()
        elif(machine_status=="printing"):
            machine.in_use = True
            if(usage):
                usage.status_message = "In Progress."
        elif(machine_status=="error"):
            usage.error = True
            usage.save()
        return HttpResponse("Status set", status=200)
        
    
def machine_temperature(request):
    pass

def machine_print(request):
    pass
    


#
## USER MANAGEMENT
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
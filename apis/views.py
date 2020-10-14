

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
from machine_management.utils import *

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

        response = clear_usage(machine)
        
        if(not response):
            return HttpResponse("Machine was not in use.", status=200)

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

        response = fail_usage(machine)
        if(not response):
            return HttpResponse("Machine was not in use.", status=200)

        return HttpResponse("Machine cleared.", status=200)
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
##start: print is starting and create machine_usage 
##error: printer errored out
@csrf_exempt
def machine_status(request):
    #if get return machine status
    if(request.method == 'GET'):
        machine_id = request.GET.get("machine_id",None)
        
        if(not machine_id):
            return HttpResponse("No machine_id provided.", status=400)
        machine_id = int(machine_id)
        
        machine = Machine.objects.get(id=machine_id)
        if(machine.current_job != None):
            return HttpResponse(machine.current_job.status_message, status=200)
        elif(machine.current_print_information != None):
            return HttpResponse(machine.current_print_information.status_message, status=200)
        else:
            return HttpResponse("Idle.", status=200)
    #if post update machine_status    
    else:
        #verify key
        if(not verify_key(request)):
            return HttpResponse("Invalid or missing API Key", status=403)
        
        #get machine id
        machine_id = request.GET.get("machine_id",None)
        if(not machine_id):
            return HttpResponse("No machine_id provided.", status=400)
        machine_id = int(machine_id)
        
        #get machine status
        machine_status = request.GET.get("status",None)
        if(not machine_status):
            return HttpResponse("No status provided.", status=400)
        
        #get machine status message
        machine_status_message = request.GET.get("status_text",None)
        if(not machine_status_message):
            return HttpResponse("No status_text provided.", status=400)
            
        #get machine
        machine = Machine.objects.get(id=machine_id)

        #get usage and print information
        usage = machine.current_job
        print_information = machine.current_print_information
        
        #if starting print
        if(machine_status=="printing"):
            #set machine to in use
            #if paost print and usage is still running clear
            information = create_print(machine)
            information.status = machine_status
            information.status_message = machine_status_message
            information.save()
            
        elif(machine_status=="completed"):
            if(print_information):
                print_information.end_time = timezone.now()
                print_information.status_message = "Completed."
                print_information.save()
                
                
                machine.current_print_information = None
                machine.save()
                
            if(usage):
                usage.complete = True
                usage.end_time = timezone.now()
                usage.status_message = "Completed."
                usage.save()
            
            if(not machine.current_print_information and not machine.current_job):
                machine.in_use = False
                machine.save()
                        
        elif(machine_status=="error"):
            if(usage):
                usage.error = True
                usage.save()
            if(print_information):
                print_information.status_message = machine_status_message
                print_information.error = True
                print_information.save()
            
        return HttpResponse("Status set", status=200)
        
@csrf_exempt  
def machine_temperature(request):
    if(request.method == 'GET'):
        machine_id = request.GET.get("machine_id",None)
        job_id = request.GET.get("job_id",None)
        if(not machine_id and not job_id):
            return HttpResponse("No machine_id or job_id provided.", status=400)
        
        print_information = None
        if(machine_id):
            machine = Machine.objects.get(id=machine_id)
            print_information = machine.current_print_information
        else:
            print_information = JobInformation.objects.get(id=job_id)
            
        if(print_information):
            output_response=[]
            print(dir(print_information))
            temperatures = print_information.tooltemperature_set.all()
            
            for tools in temperatures:
                tool_information = {
                    "tool_time":str(tools.tool_time),
                    "tool_name":tools.tool_name,
                    "tool_temperature":tools.tool_temperature,
                    "tool_temperature_goal":tools.tool_temperature_goal
                }
                output_response.append(tool_information)
            return HttpResponse(json.dumps(output_response), status=200)
        return HttpResponse("No PrintInformation", status=400)
           
        
        
    elif(request.method == 'POST'):
        if(not verify_key(request)):
            return HttpResponse("Invalid or missing API Key", status=403)
            
        temperature_data = json.loads(request.body)
        
        
        machine_id = request.GET.get("machine_id",None)
        if(not machine_id):
            return HttpResponse("No machine_id provided.", status=400)
        machine_id = int(machine_id)          
        machine = Machine.objects.get(id=machine_id)
        print_information = machine.current_print_information
        for tool in temperature_data:
            temperature = ToolTemperature()
            temperature.machine = machine
            temperature.tool_name = tool["tool_name"]
            temperature.tool_temperature = tool["temperature"]
            temperature.tool_temperature_goal = tool["goal"]
            if(print_information):
                temperature.job = print_information
            temperature.save()
            
        return HttpResponse("Data recorded", status=200)
    return HttpResponse("Invalid request", status=405)
    
@csrf_exempt  
def machine_information(request):
    if(request.method == 'GET'):
        machine_id = request.GET.get("machine_id",None)
        if(not machine_id):
            return HttpResponse("No machine_id provided.", status=400)
        machine_id = int(machine_id)          
        machine = Machine.objects.get(id=machine_id)
        
        usage = machine.current_job
        
        response = {'status':"No job running"}
        if(usage):
            response['status'] = usage.status_message
            response['start_time'] = usage.start_time
            response['completion_time'] = usage.end_time
            
            
        return HttpResponse(json.dumps(response), status=200)
            
    if(request.method == 'POST'):
        if(not verify_key(request)):
            return HttpResponse("Invalid or missing API Key", status=403)
        
        

        machine_id = request.GET.get("machine_id",None)
        if(not machine_id):
            return HttpResponse("No machine_id provided.", status=400)
        machine_id = int(machine_id)          
        machine = Machine.objects.get(id=machine_id)
        
        end_time = request.GET.get("end_time",None)
        file_id =  request.GET.get("file_id",None)

        print_information = machine.current_print_information
        if(print_information):
            if(end_time):
                time_information = end_time.split('.')[0]
                print_information.end_time = datetime.strptime(time_information, "%Y-%m-%d %H:%M:%S")
                print_information.save()
            
            if(file_id):
                print_information.file_id = file_id
                print_information.save()
        else:
            information = create_print(machine)
            
            if(end_time):
                time_information = end_time.split('.')[0]
                information.end_time = datetime.strptime(time_information, "%Y-%m-%d %H:%M:%S")
            
            if(file_id):
                information.file_id = file_id
                
            information.save()
            
        return HttpResponse("Data recorded", status=200)

    return HttpResponse("Invalid request", status=405)
    


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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
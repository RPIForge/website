

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
#   Machine API
#

# ! type: POST
# ! function: clears usage running on machine
# ? required: machine_id
# ? returns: HTTP response
# TODO: Fix csrf_exempt requirement and make sure machine with id exists
# TODO: before getting the object
@csrf_exempt # TODO FIX THIS
@login_required
def clear_machine(request):
    if request.method == "POST":
        #get post data
        data = json.loads(request.body)

        if "machine_id" not in data:
            return HttpResponse("No machine_id provided.", status=400)

        #get machine object id
        #TODO make sure machine with id exists
        machine = Machine.objects.get(id=int(data["machine_id"]))

        if not machine.in_use:
            return HttpResponse("Machine was not in use.", status=200)

        #get the current usage and clear it
        usage = machine.current_job
        usage.clear_time = timezone.now()
        usage.complete = True
        if (not usage.error) and (not usage.failed):
            usage.status_message = "Cleared."
        usage.save()

        #clear machine
        machine.current_job = None
        machine.in_use = False
        machine.save()
        return HttpResponse("Machine cleared.", status=200)
    else:
        return HttpResponse("", status=405) # Method not allowed


# ! type: POST
# ! function:  fail a machine usage and send email
# ? required: machine id
# ? returns: HTTP Respose
# TODO: Fix csrf_exempt requirement and make sure machine with id exists
# TODO: before getting the object
@csrf_exempt # TODO FIX THSI
@login_required
def fail_machine(request):
    if request.method == "POST":
        data = json.loads(request.body)

        if "machine_id" not in data:
            return HttpResponse("No machine_id provided.", status=400)

        #get machine from post data
        machine = Machine.objects.get(id=int(data["machine_id"]))

        if not machine.in_use:
            return HttpResponse("Machine was not in use.", status=200)

        #get and fail machine usage
        usage = machine.current_job
        usage.clear_time = timezone.now()
        usage.failed = True
        usage.status_message = "Failed."
        usage.save()

        #send failed print email
        utils.send_failure_email(usage)
        return HttpResponse("Machine marked as failed.", status=200)
    else:
        return HttpResponse("", status=405) # Method not allowed


# ! type: GET/POST
# ! function: Get a list of machines and submit usage information. This was primarily
# ! used by the old machine_usage form. 
# ? required: None
# ? returns: HTTP Response 
# TODO: Remove this method as it is depreciated in the buisness update
@csrf_exempt 
def machine_endpoint(request):
    #get machine information
    if request.method == 'GET':
        output = []

        machines = Machine.objects.all().order_by("machine_name")

        #loop through all active machiens
        for m in machines:
            if not m.deleted:
                #get information about the machine
                machine_entry = {
                    "name": m.machine_name,
                    "in_use": m.in_use,
                    "enabled": m.enabled,
                    "status": m.status_message,
                    "usage_policy": m.machine_type.usage_policy,
                    "hourly_cost": float(m.machine_type.hourly_cost),
                    "slots": []
                }

                #get information about all of the slots in the machines
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

    #create machine usage
    elif request.method == 'POST':
        return create_machine_usage(request) # Make sure this still checks for login!
    else:
        return HttpResponse("", status=405) # Method not allowed
        
#
#   Users API
#

# ! type: GET
# ! function: verify if a user with uuid exists and gives their role. This helps other sites authenticate
# ! against us 
# ? required: user uuid
# ? returns: HTTP Response
# TODO Return list of groups not highest group
def verify_user(request):
    if request.method == 'GET':
        # get user asociated with uuid
        uuid = request.GET.get('uuid', '')
        try:
            userprofile = UserProfile.objects.get(uuid=uuid)
        except  UserProfile.DoesNotExist:
            return HttpResponse(status=204)
        except ValidationError:
            return HttpResponse(status=404)
        
        #get user from userprofile
        user = userprofile.user
        
        #return most senior group. Change this to list of groups
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
#   Volunteers
#    

# ! type: GET
# ! function: Get the list of current volunteers on duty
# ? required: None
# ? returns: HTTP Response 
# TODO: None
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
#    Billing
#

       
# ! type: GET
# ! function: Get list of charges for the semester for either graduating or nongraduating students
# ? required: semester_id
# ? returns: csv of charges
# TODO: Improve speed as this strains the server. Change how membership cost is applied.
def charge_sheet(request):
    if request.method == 'GET':
        #get get paramters
        graduating = request.GET.get('graduating', False)
        semester_id = request.GET.get('semester_id', None)

        
        #semester id is required
        if(not semester_id):
            return HttpResponse("No Semester Provided.", status=400) 
        
        semester = Semester.objects.get(id=semester_id)
        
        
        #get the list of users depneidng on if they are graduating
        #We charge memebrs differently if they are graduating or not.
        if(graduating=='true'):
            usages = semester.usage_set.filter(userprofile__is_graduating=True)
            
            remaining_users = list(User.objects.filter(userprofile__is_graduating=True, groups__name='member'))
            
            graduating_string = 'graduating'
        else:
            usages = semester.usage_set.filter(userprofile__is_graduating=False)
            
            remaining_users = list(User.objects.filter(userprofile__is_graduating=False, groups__name='member'))
            
            graduating_string = 'nongraduating'
          
        
        
        #if data reading has already been done update
        
        #set up variables
        total_revenue = 0
        user_dict = {}
        
        
        #for all usages in the semester
        for usage in usages:
            #get user name and cost
            name = usage.userprofile.user.get_full_name()
            cost = usage.cost()
            
            #remove them from the list of users left
            if(usage.userprofile.user in remaining_users):
                remaining_users.remove(usage.userprofile.user)
            
            #either create dict or update balance
            if(name in user_dict):
                user_dict[name]['balance'] = float(user_dict[name]['balance']) + float(cost)
            else:
                user_dict[name] = {'rin':usage.userprofile.rin, 'balance':float(cost+15)}
                
            total_revenue = float(total_revenue) + float(cost) + float(15)
        
        for user in remaining_users:
            user_dict[user.get_full_name()] = {'rin':user.userprofile.rin, 'balance':float(15)}
            
        
        
        #set up csv response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}_{}_{}.csv"'.format(semester.season, semester.year, graduating_string)
        
        writer = csv.writer(response)
        
        #generate csv data from user_dictionary
        csv_data = [['Full Name','Rin', 'Balance']]
        for user in user_dict:
            user_info = user_dict[user]
            csv_data.append([user, user_info['rin'], user_info['balance']])
            
        #write rows to csv
        writer.writerows(csv_data)
        
        return response

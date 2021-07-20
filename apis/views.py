

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

        response = clear_usage(machine)
        response = response or clear_print(machine)
        
        if(not response):
            return HttpResponse("Machine was not in use.", status=200)

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

        response = fail_usage(machine)
        if(not response):
            return HttpResponse("Machine was not in use.", status=200)

        return HttpResponse("Machine cleared.", status=200)
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

        #get machine id
        machine_id = request.GET.get("machine_id",None)
        if(not machine_id):
            return HttpResponse("No machine_id provided", status=400)
        machine_id = int(machine_id)

        #get machine object
        try:
            machine = Machine.objects.get(id=machine_id)
        except ObjectDoesNotExist:
            return HttpResponse("Machine not found", status=400)

        data = {
            'name':machine.machine_name,
            'type':machine.machine_type.machine_type_name,
            'id':machine.id
        }

        if(machine.current_print_information):
            data["job"] = str(machine.current_print_information)
            data["job_id"] = machine.current_print_information.id
        
        if(machine.current_job):
            slot_usage = machine.current_job.slotusage_set.all()[0]
            resource = slot_usage.resource
            data["material"] = str(resource)

        return HttpResponse(json.dumps(data))

# ! type: HELPER
# ! funciton: verify that a request has a valid API key
# ? required: HTTP Request
# ? returns: boolean
# TODO:
def verify_key(request):
    if("X-Api-Key" in request.headers):
        return Key.objects.filter(key=request.headers["X-Api-Key"]).exists()
    return False



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
        organization_id = request.GET.get('organization_id', None)

        
        #semester id is required
        if(not semester_id):
            return HttpResponse("No Semester Provided.", status=400) 
        
        org = None
        if(organization_id is not None):
            org = Organization.objects.filter(org_id=organization_id).first()
            if(org is None):
                return HttpResponse("Invalid Organization Provided", status=400) 

        semester = Semester.objects.filter(id=semester_id).first()
        if(semester is None):
            return HttpResponse("Invalid Semester Provided", status=400) 
        
        
        #get the list of users depneidng on if they are graduating
        #We charge memebrs differently if they are graduating or not.
        if(graduating=='true'):
            usages = semester.get_usages().filter(userprofile__is_graduating=True)
            remaining_users = set(User.objects.filter(userprofile__is_graduating=True, groups__name='member'))
            
            graduating_string = 'graduating'
        else:
            usages = semester.get_usages().filter(userprofile__is_graduating=False)
            remaining_users = set(User.objects.filter(userprofile__is_graduating=False, groups__name='member'))
            
            graduating_string = 'nongraduating'
          
        if(org):
            usages = usages.filter(organization=org)
        
        
        #if data reading has already been done update
        
        #set up variables
        total_revenue = 0
        user_dict = {}
        org_dict = {}
        
        
        #for all usages in the semester
        for usage in usages:
            user_profile = usage.userprofile
            user = user_profile.user

            #get user name and cost
            name = user.get_full_name()
            cost = usage.cost()

            if(usage.machine.organization.name not in org_dict):
                org_dict[usage.machine.organization.name] = 0

            org_dict[usage.machine.organization.name]+=float(cost)

            #remove them from the list of users left
            if(user in remaining_users):
                remaining_users.remove(user)
            
            

            #either create dict or update balance
            if(name in user_dict):
                user_balance = float(user_dict[name]['balance'])
                user_dict[name]['balance'] =  user_balance + float(cost)
            else:
                user_dict[name] = {'rin':usage.userprofile.rin}
                
                if(org):
                    user_dict[name]['balance'] = float(cost) + org.membership_fee
                else:
                    user_dict[name]['balance'] = float(cost) + user_profile.get_organization_fees()
                
            total_revenue = float(total_revenue) + float(cost)
        
        for user in remaining_users:
            balance = user.userprofile.get_organization_fees()
            if(org):
                balance = org.membership_fee

            user_dict[user.get_full_name()] = {'rin':user.userprofile.rin, 'balance':balance}
            
        
        
        #set up csv response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}_{}_{}.csv"'.format(semester.season, semester.year, graduating_string)
        
        writer = csv.writer(response)
        
        #generate csv data from user_dictionary
        if(org):
            csv_data = [['Organization',org.name]]
        else:
            csv_data = []
        
        csv_data.append(['Full Name','Rin', 'Balance'])

        for user in user_dict:
            user_info = user_dict[user]
            csv_data.append([user, user_info['rin'], user_info['balance']])
            
        if(org):
            csv_data.append(['','Organization Fee',org.organization_fee])
            csv_data.append(['','Total Cost',total_revenue + org.organization_fee])
        else:
            csv_data.append(['','Gross Revenue', total_revenue])
            
            for org in org_dict:
                csv_data.append(['',org.strip().title()+' Revenue',org_dict[org]])
        #write rows to csv
        writer.writerows(csv_data)
        
        return response


#
#   Organizations
#    

# ! type: POST
# ! function: Add user to organization
# ? required: None
# ? returns: HTTP Response 
# TODO: None
def join_organization(request):
    if request.method == 'POST':
        try:
            json_data = json.loads(request.body)
        except json.decoder.JSONDecodeError:
            return HttpResponse('Invalid Data',status=400)

        #get organization
        org_id = json_data['org_id']
        org = Organization.objects.filter(org_id=org_id).first()

        if(org is None):
            return HttpResponse('Org does not exist',status=400)

        #get user
        user = request.user

        #join organization
        obj = org.add_user(user)
        if(obj is None):
            response = HttpResponse('rin_required',status=400)
            response.reason_phrase = 'rin_required'
            return response

        return HttpResponse('')
            
#

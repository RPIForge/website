

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
     


def verify_key(request):
    if("X-Api-Key" in request.headers):
        return Key.objects.filter(key=request.headers["X-Api-Key"]).exists()
    return False



#
# Octoprint Functions
#

# ! type: HELPER
# ! function: Handle status updates
# ? required: Machine, machine status, status message
# ? returns: nothing
# TODO:
@csrf_exempt
def handle_status(machine, machine_status, machine_status_message):
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
    #if completed 
    elif(machine_status=="completed"):
        #if there is a print_information then complete it
        if(print_information):
            print_information.end_time = timezone.now()
            print_information.status_message = "Completed."
            print_information.save()
            
            
            machine.current_print_information = None
            machine.save()
            
        #if there is a usage complete it
        if(usage):
            usage.complete = True
            usage.end_time = timezone.now()
            usage.status_message = "Completed."
            usage.save()
        
        #if nothing attached to machine then set it not in use
        if(not machine.current_print_information and not machine.current_job):
            machine.in_use = False
            machine.save()
    
    #if error then set error messages
    elif(machine_status=="error"):
        if(usage):
            usage.error = True
            usage.save()
        if(print_information):
            print_information.status_message = machine_status_message
            print_information.error = True
            print_information.save()
    
    else:
        if(print_information):
            print_information.status_message = machine_status_message
            print_information.save()
        else:
            machine.status_message = machine_status_message
            machine.save()
    
# ! type: HELPER
# ! function: Handle informatino updates
# ? required: Machine, [end_time, file_id]
# ? returns: nothing
# TODO:
def handle_information(machine, end_time,file_id):
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

# ! type: HELPER
# ! function: Handle new etmperature informatino
# ? required: Machine, temperature data
# ? returns: nothing
# TODO:
def handle_temperature(machine, temperature_data):
    #get print information if there is one
    print_information = machine.current_print_information
    for tool in temperature_data:
        #create new temperature and attach it to machine
        temperature = ToolTemperature()
        temperature.machine = machine
        temperature.name = tool["tool_name"]
        temperature.temperature = tool["temperature"]
        temperature.temperature_goal = tool["goal"]
        
        #if print information then attach it to
        if(print_information):
            temperature.job = print_information
        temperature.save()

# ! type: HELPER
# ! function: Handle new location informatino
# ? required: Machine, current_height, current_layer, max_layer
# ? returns: nothing
# TODO:
def handle_location(machine, current_height, current_layer, max_layer):
    print_information = machine.current_print_information

    if(current_height is '-'):
        current_height = 0

    if(current_layer is '-'):
        current_layer = 0

    if(max_layer is '-'):
        max_layer = 0

    location_data = LocationInformation()
    location_data.layer = current_layer
    location_data.max_layer = max_layer
    location_data.z_location = current_height

    location_data.machine = machine
    if(print_information):
        location_data.job = print_information
    location_data.save()

## This is the format for the data to be recieved
#{
#    'time':datetime
#    'data':{
#        'machine':{
#            'status':string
#            'status_message':string
#        },
#        'print':{
#            'end_time':datetime
#            'file_id':string
#        }
#        'temperature': {
#            'tool_name':{
#                'current':float
#                'goal':float
#            }
#            ...
#        },
#
#        'location': {
#            'current_height':int
#            'current_layer':int
#            'max_layer':int
#            ''
#        }
#    }
#}

# ! type: GET/POST
# ! function: Update machine Data
# ? required: API Key, machine_id, Data Dict
# ? returns: HTTP Response
# TODO:
@csrf_exempt
def machine_data(request):
    if(request.method == 'GET'):
        pass
    elif(request.method == 'POST'):
        #verify key
        if(not verify_key(request)):
            return HttpResponse("Invalid or missing API Key", status=403)
        
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

        printer_dict = json.loads(request.body)
        data_time = printer_dict['time']
        data = printer_dict['data']

        #handle new machine data
        if('machine' in data):
            machine_status = data['machine']['status']
            machine_status_message = data['machine']['status']
            handle_status(machine,machine_status,machine_status_message)

        #handle print update information
        if('print' in data):
            end_time = data['print'].get('end_time',None)
            file_id = data['print'].get('file_id',None)
            handle_information(machine,end_time,file_id)
        
        #handle new temperature information
        if('temperature' in data):
            temperature_data = data["temperature"]
            handle_temperature(machine,temperature_data)

        #handle location
        if('location' in data):
            height = data["location"]["current_height"]
            layer = data["location"]["current_layer"]
            max_layer = data["location"]["max_layer"]

            handle_location(machine,height,layer,max_layer)
        
        return HttpResponse("Data Set", status=200)
    return HttpResponse("Invalid request", status=405)

        
# ! type: GET
# ! function: Either get machine status
# ? required: API Key, machine_id/API, machine_id,status
# ? returns: HTTP Response
# TODO:
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
    
# ! type: GET
# ! function: View temperature infromation
# ? required: Machine or Job/Temperature information
# ? returns: HTTP Rendered Template/HTTP Response
# TODO: Make Generic
@csrf_exempt  
def machine_temperature(request):
    #if get
    if(request.method == 'GET'):
        #get varlables from url
        machine_id = request.GET.get("machine_id",None)
        job_id = request.GET.get("job_id",None)
        display_type = request.GET.get("display_graph",None)
        
        
        if(not machine_id and not job_id):
            return HttpResponse("No machine_id or job_id provided.", status=400)
        
        #get the current print_information or get previous print information
        print_information = None
        if(machine_id):
            machine = Machine.objects.get(id=machine_id)
            print_information = machine.current_print_information
            if(not print_information and machine.current_job):
                usage = machine.current_job
                print_information = usage.current_print_information
        else:
            print_information = JobInformation.objects.get(id=job_id)
            
        #if there is such information
        if(print_information):
            #get all temperatures for the print
            temperatures = print_information.tooltemperature_set.all().order_by('time')

            
            #if raw data requested
            if(not display_type):
                #get raw data in json
                output_response=[]
                for tools in temperatures:
                    tool_information = {
                        "tool_time":str(tools.time),
                        "tool_name":tools.name,
                        "tool_temperature":tools.temperature,
                        "tool_temperature_goal":tools.temperature_goal
                    }
                    output_response.append(tool_information)
                
                return HttpResponse(json.dumps(output_response), status=200)
            else:
                #format temperature to be displayed
                temperature_information={
                    "time":[],
                    "data":{}
                }
                for tools in temperatures:
                    if tools.name in temperature_information["data"]:
                        if(tools.time.strftime('%H:%M:%S') not in temperature_information["time"]):
                            temperature_information["time"].append(tools.time.strftime('%H:%M:%S'))
                        
                        temperature_information["data"]["{} goal".format(tools.name)].append(tools.temperature_goal)
                        temperature_information["data"]["{}".format(tools.name)].append(tools.temperature)

                    else:
                        temperature_information["data"]["{} goal".format(tools.name)] = [tools.temperature_goal]
                        temperature_information["data"]["{}".format(tools.name)] = [tools.temperature]


                        
                return render(request, 'apis/data_graph.html', {"title": "Machine Temperature", "units":"Degrees (C)", "data_history":json.dumps(temperature_information)})
            
        if(display_type):
                return render(request, 'apis/data_graph.html', {"data_history":json.dumps({})})
        return HttpResponse("No PrintInformation", status=400)
           
    return HttpResponse("Invalid request", status=405)

# ! type: GET
# ! function: View Height/Layer infromation
# ? required: Machine or Job/Height-Layer information
# ? returns: HTTP Rendered Template
# TODO: Make Generic
@csrf_exempt  
def machine_location(request):
    #if get
    if(request.method == 'GET'):
        #get varlables from url
        machine_id = request.GET.get("machine_id",None)
        job_id = request.GET.get("job_id",None)
        display_type = request.GET.get("display_graph",None)
        
        
        if(not machine_id and not job_id):
            return HttpResponse("No machine_id or job_id provided.", status=400)
        
        #get the current print_information or get previous print information
        print_information = None
        if(machine_id):
            machine = Machine.objects.get(id=machine_id)
            print_information = machine.current_print_information
            if(not print_information and machine.current_job):
                usage = machine.current_job
                print_information = usage.current_print_information
        else:
            print_information = JobInformation.objects.get(id=job_id)
            
        #if there is such information
        if(print_information):
            #get all temperatures for the print
            locations = print_information.locationinformation_set.all()

            
            #if raw data requested
            if(not display_type):
                #get raw data in json
                output_response=[]
                for location in locations:
                    location_information = {
                        "time":str(tools.time),
                        "layer":location.layer,
                        "max_layer":location.max_layer,
                        "z-location":location.z_location,
                        "tool_temperature_goal":tools.temperature_goal
                    }
                    output_response.append(location_information)
                
                return HttpResponse(json.dumps(output_response), status=200)
            else:
                #format temperature to be displayed
                location_information={
                    "time":[],
                    'data':{
                        'layer': [],
                        'max-layer': [],
                        'z': []
                    }
                }
                for location in locations:
                    if(location.time.strftime('%H:%M:%S') not in location_information["time"]):
                        location_information["time"].append(location.time.strftime('%H:%M:%S'))
                    
                    location_information["data"]["layer"].append(location.layer)
                    location_information["data"]["max-layer"].append(location.max_layer)
                    location_information["data"]["z"].append(location.z_location)

                        
                return render(request, 'apis/data_graph.html', {"title": "Machine Location", "units":"Distance (mm)", "data_history":json.dumps(location_information)})
            
        if(display_type):
                return render(request, 'apis/data_graph.html', {"data_history":json.dumps({})})
        return HttpResponse("No PrintInformation", status=400)
           
   
    return HttpResponse("Invalid request", status=405)

# ! type: GET/POST
# ! function: View general infromation/Update general informaiton
# ? required: Machine or Job/Temperature information
# ? returns: HTTP Response
# TODO:  
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

    return HttpResponse("Invalid request", status=405)
    


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

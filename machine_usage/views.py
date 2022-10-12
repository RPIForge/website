# Importing Django Utils
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models.base import ObjectDoesNotExist
from django.utils import timezone
from django.conf import settings

# Importing Models
from machine_management.models import *
from django.contrib.auth.models import User, Group

# Import Forms
from machine_usage.forms import *

# Importing Other Libraries
import json
from datetime import datetime
from decimal import Decimal
from datetime import datetime, timedelta
from machine_management import utils

import requests

# ! type: Helper Function
# ! function: Validates a machine usage's json  
# ? required: dictionary
# ? returns: tuple of success and error message
# TODO: Remove after buisness update sepeartes usage
def validate_machine_usage_json(json_dict):
    if not (type(json_dict) == dict):
        return (False, "Root JSON object was not a dictionary.")

    field_types = [("machine_name", str), ("slot_usages", list), ("hours", int), ("minutes", int)]

    for (name, expected_type) in field_types:
        if name not in json_dict:
            return (False, f"Parameter {name} was not found in dictionary.")

        if not (type(json_dict[name]) == expected_type):
            return (False, f"Parameter {name} was provided as type {type(json_dict[name])} (expected {expected_type}).")

    return (True, "")

# ! type: Helper function
# ! function: Validates if a machine is in use and its slots
# ? required: machine object and list of slost
# ? returns: Boolean
# TODO: Remove after buisness removes usage from the frontend
def validate_machine(machine, slot_usages):
    input_set = set()
    model_set = set()

    for u in slot_usages:
        input_set.add(u["name"])

    model_names = machine.machine_type.get_slot_names()

    for n in model_names:
        model_set.add(n)

    return (input_set == model_set) and not machine.in_use

# ! type: Helper function
# ! function: Validates if a slot usage is a valid usage
# ? required: slot, material used, amount of resource
# ? returns: Boolean
# TODO: Remove in buisness update
def validate_slot(slot, material, quantity):
    try:
        qty = Decimal(quantity)
        if qty < 0:
            print("Negative Quantity")
            return False
    except Exception as e:
        print(f"Quantity not a Decimal. Exception: {e}")
        return False
    
    if slot.resource_allowed(material):
        return True
    else:
        print("Resource not allowed in slot")
        return False

# ! type: POST
# ! function: create machine usage from a request 
# ? required: Usage POST Data
# ? returns: HTTP Response
# TODO: Remove in buisness update
@login_required
def create_machine_usage(request):
    
    
    '''if request.method == 'POST':
        data = json.loads(request.body)
        machine_name = data["machine_name"]
        machine = Machine.objects.get(machine_name=machine_name)

        validation_result = validate_machine(machine, data["slot_usages"])

        if not validation_result:
            print(f"Invalid machine or schema. JSON: {request.body}")
            return HttpResponse("Invalid machine or schema.", status=400)

        if not "for_class" in data:
            return HttpResponse("for_class missing from object.", status=400)

        if not "own_material" in data:
            return HttpResponse("own_material missing from object.", status=400)

        if not "is_reprint" in data:
            return HttpResponse("is_reprint missing from object.", status=400)

        if not "hours" in data:
            return HttpResponse("hours missing from object.", status=400)

        if not "minutes" in data:
            return HttpResponse("minutes missing from object.", status=400) # TODO Better verification...

        for_class = data["for_class"]
        own_material = data["own_material"]
        is_reprint = data["is_reprint"]

        slot_usages = []

        for slot_usage in data["slot_usages"]: # TODO Ensure that data["slot_usages"] is actually iterable. Or alternatively validate the JSON somewhere. List of dicts.
            slot_name = slot_usage["name"]
            resource = slot_usage["resource"]
            quantity = slot_usage["quantity"]

            slot = machine.machine_type.get_slot(slot_name)

            validation_result = validate_slot(slot, resource, quantity)
            if not validation_result:
                print(f"Quantity for slot {slot_name} was not a valid decimal, or the resource provided was invalid. JSON: {request.body}")
                return HttpResponse(f"Quantity for slot {slot_name} was not a valid decimal, or the resource provided was invalid.", status=400)

            su = SlotUsage()
            slot_usages.append(su)
            su.machine_slot = slot
            su.resource = Resource.objects.get(resource_name=resource)
            su.amount = Decimal(quantity)

        u = Usage()
        u.semester = Semester.objects.get(current=True)
        u.machine = machine
        u.userprofile = request.user.userprofile
        u.save() # Necessary so start_time gets set to current time before referencing it below
        u.set_end_time(float(data["hours"]), float(data["minutes"]))

        u.for_class = for_class
        u.own_material = own_material
        u.is_reprint = is_reprint

        u.save()
        
        for su in slot_usages:
            su.usage = u
            su.save()

        machine.in_use = True
        machine.current_job = u

        print_information = machine.current_print_information
        if(print_information):
            if(print_information.start_time < timezone.now() - timedelta(minutes = 30)):
                clear_print(machine)
                print_information=None
            else:
                print_information.usage = u
                print_information.save()
                
                u.current_print_information = print_information
                u.save()
                
        machine.save()

        return HttpResponse("Usage successfully recorded.", status=200)
    else:
        return HttpResponse("", status=405) # Method not allowed'''


# ! type: GET
# ! function:  Generates machine usage form
# ? required: None
# ? returns: HTTP Rendered Template
# TODO:
@login_required
def machine_usage(request):
    return MachineUsageWizard.as_view([MachineSelectionForm, MachineSlotUsageForm])
    
    '''
    machines = Machine.objects.all().filter(deleted=False, in_use=False, enabled=True).order_by("machine_name")
    available_machines = {}

    for m in machines:
        if (not m.deleted) and (not m.in_use):
            type_name = m.machine_type.machine_type_name
            if type_name not in available_machines:
                available_machines[type_name] = []
            available_machines[type_name].append(m.machine_name)

    return render(request, 'machine_usage/forms/machine_usage.html', {"available_machines":available_machines})
    '''

# ! type:  GET
# ! function: Generate resource usage form
# ? required: Machine name
# ? returns: HTTP Rendered Template
# TODO: Remove in buisness Update
@login_required
def generate_machine_form(request):
    machine_name = request.GET.get("machine", None)
    if machine_name is None:
        return HttpResponse("Machine name not found.", status=400)

    machine = Machine.objects.get(machine_name=machine_name) # TODO Catch machine not existing
    slots = []

    for slot in machine.machine_type.machineslot_set.all():
        if not slot.deleted:
            allowed_resources = []

            for resource in slot.allowed_resources.all():
                if resource.in_stock and not resource.deleted:
                    allowed_resources.append({
                        "name":resource.resource_name,
                        "unit":resource.unit
                    })

            slots.append({
                "name":slot.slot_name,
                "allowed_resources":allowed_resources
            })

    return render(request, 'machine_usage/forms/machine_form.html', {"slots":sorted(slots, key=lambda k: k["name"]), "machine_name":machine_name})


# ! type: GET/POST
# ! function: Generate or Execute clearing machine
# ? required: /Machine name
# ? returns: HTTP Rendered Template/redirect
# TODO: Verify user is volunteer or above
@login_required #TODO This should only be available to volunteers and up.
def generate_clear_machine_form(request):
    if request.method == 'GET':
        machines_in_use = Machine.objects.filter(in_use=True)
        output = {}

        for m in machines_in_use:
            type_name = m.machine_type.machine_type_name
            if type_name not in output:
                output[type_name] = []
            output[type_name].append(m.machine_name)

        return render(request, 'machine_usage/forms/clear_machine.html', {"machines_in_use":output})
    else:
        machine_name = request.POST["machine_name"]
        machine = Machine.objects.get(machine_name=machine_name)

        usage = machine.current_job
        usage.clear_time = timezone.now()
        usage.complete = True
        if (not usage.error) and (not usage.failed):
            usage.status_message = "Cleared."
        usage.save()

        machine.current_job = None
        machine.in_use = False
        machine.save()
        return redirect('/forms/clear_machine')

# ! type: GET/POST
# ! function: Generate or Execute failing a machine
# ? required: None/machine_name
# ? returns: HTTP Rendered Template/redirect
# TODO: Verify user is volunteer
@login_required #TODO This should only be available to volunteers and up.
def generate_failed_usage_form(request):
    if request.method == 'GET':
        machines_in_use = Machine.objects.filter(in_use=True).filter(current_job__failed=False)
        output = {}

        for m in machines_in_use:
            type_name = m.machine_type.machine_type_name
            if type_name not in output:
                output[type_name] = []
            output[type_name].append(m.machine_name)

        return render(request, 'machine_usage/forms/failed_usage.html', {"machines_in_use":output})
    else:
        if(not verify_key(request)):
            return HttpResponse("Invalid or missing API Key", status=403)

        machine_name = request.POST["machine_name"]
        machine = Machine.objects.get(machine_name=machine_name)

        fail_log = {
            "machine": machine_name,
            "user": request.user.get_username(),
            "filament": request.POST["filament_type"],
            "percentage": request.POST["percentage"],
            "error_msg": request.POST["error_msg"],
            "observed_failure": request.POST.getlist("failure_type")
        }

        if request.POST.getlist("failure_type").count("other") > 0:
            fail_log["observed_failure"].append(request.POST["other_failure"])

        try:
            r = requests.post(settings.FAILURE_FORM_URL, json = fail_log)
        except requests.exceptions.RequestException as e:
            print(e)

        utils.fail_usage(machine)
        return redirect('/dyn/volunteer_dashboard')

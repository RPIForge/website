# Importing Django Utils
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models.base import ObjectDoesNotExist

# Importing Models
from machine_usage.models import *
from django.contrib.auth.models import User, Group

# Importing Forms
from machine_usage.forms import ForgeUserCreationForm, ForgeProfileCreationForm

# Importing Helper Functions
import machine_usage.utils as utils

# Importing Other Libraries
import json
from decimal import Decimal
from datetime import datetime

#
#   Pages/Login
#

def render_equipment(request):
    return render(request, 'machine_usage/equipment.html', {})

def render_hours(request):
    return render(request, 'machine_usage/hours.html', {})

def render_index(request):
    return render(request, 'machine_usage/index.html', {})

def render_login(request):
    if request.method == 'GET':

        if request.user.is_authenticated:
            return redirect('/myforge')
        else:
            return render(request, 'machine_usage/login.html', {})

    elif request.method == 'POST':

        rcs_id = request.POST['rcsid']
        password = request.POST['password']

        user = authenticate(request, username=rcs_id, password=password)

        if user is not None:
            login(request, user)
            return redirect('/myforge')
        else:
            return render(request, 'machine_usage/login.html', {"error":"Login failed."})
 
def render_news(request):
    return render(request, 'machine_usage/news.html', {}) # TO-DO: Implement the "News" page.

def render_our_space(request):
    return render(request, 'machine_usage/index.html', {}) # TO-DO: Implement the "Our Space" page.

def render_status(request):
    return render(request, 'machine_usage/index.html', {}) # TO-DO: Implement the "Status" page.

def render_verify_email(request):
    # Make sure we only support GET requests, so we can make POST do something later if needed
    if request.method == 'GET':
        # Get the verification token from the request, or a NoneType if the request is malformed.
        token = request.GET.get("token", None)
        
        if token is None:
            return render(request, 'machine_usage/verify_email.html', {"has_message":True, "message_type":"error", "message":"Invalid Request: No token provided."})
            
        # See if we have a user that corresponds to the token.
        try:
            user_profile = UserProfile.objects.get(email_verification_token=token)
        except ObjectDoesNotExist:
            return render(request, 'machine_usage/verify_email.html', {"has_message":True, "message_type":"error", "message":"Invalid Token."})

        user = user_profile.user
        
        if(user.groups.filter(name="verified_email")):
            return render(request, 'machine_usage/verify_email.html', {"has_message":True, "message_type":"info", "message":"Email already verified."})
        else:
            group = Group.objects.get(name="verified_email") # TODO Create this group if it doesn't exist - current solution is to add the group manually from the admin panel.
            user.groups.add(group)
            user.save()
            return render(request, 'machine_usage/verify_email.html', {"has_message":True, "message_type":"success", "message":"Successfully verified email!"}) 

       
@login_required
def render_myforge(request):
    if not request.user.userprofile.is_active:
        return redirect('/begin_semester')

    if not request.user.groups.filter(name="verified_email").exists():
        return redirect('/unverified_email')

    return render(request, 'machine_usage/myforge.html', {})

@login_required
def render_unverified_email(request):
    if request.user.groups.filter(name="verified_email").exists():
        return redirect('/myforge')
    return render(request, 'machine_usage/unverified_email.html', {})

@login_required
def render_begin_semester(request):
    if request.method == "GET":
        return render(request, 'machine_usage/begin_semester.html', {})
    elif request.method == "POST":
        profile = request.user.userprofile

        if request.POST["accepts_charges"] == "yes":
            profile.is_active = True
        else:
            profile.is_active = False

        if request.POST["is_graduating"] == "yes":
            profile.is_graduating = True
        else:
            profile.is_graduating = False

        profile.save()
        return redirect('/myforge')

@login_required
def resend_email_verification(request):
    if not request.user.groups.filter(name="verified_email").exists():
        print(f"Sending verification email to {request.user.email}")
        utils.send_verification_email(request.user)
    return redirect('/myforge')

def log_out(request):
    logout(request)
    return redirect('/')


#
#   Forms/Tables
#

#
#   TODO: This checks for login, but not for admin! Make sure only admins have access to these views.
#

def format_usd(fp):
    return f"${fp:.2f}"

@login_required
def list_projects(request):

    #
    # TODO: Display this on a template that doesn't show actions - e.g. is read-only.
    #

    user_profile = request.user.userprofile

    context = {
        "table_headers":["Date", "Machine", "Cost"],
        "table_rows":[],
        "page_title":"Projects"
    }

    usages = user_profile.usage_set.all()
    for u in usages:
        context["table_rows"].append([u.start_time, u.machine.machine_name, format_usd(u.cost())])

    return render(request, 'machine_usage/forms/list_items.html', context)

@login_required
def list_machines(request):
    context = {
        "table_headers":["Name", "Category", "Type", "Status Message", "Enabled", "In Use?"],
        "table_rows":[],
        "page_title":"Machines"
    }

    machines = Machine.objects.all()
    for m in machines:
	    context["table_rows"].append([m.machine_name, m.machine_type.machine_category, m.machine_type.machine_type_name, m.status_message, m.enabled, m.in_use])

    return render(request, 'machine_usage/forms/list_items.html', context)

@login_required
def list_machine_types(request):
    context = {
	    "table_headers":["Type", "Category", "Slots", "Count", "Resource Types"],
	    "table_rows":[],
        "page_title":"Machine Types"
    }

    machine_types = MachineType.objects.all()
    for m in machine_types:

            slots = m.machineslot_set.all()
            resource_set = set() # We use this to get a set of unique resources for display, since multiple slots can accept the same resource.

            for s in slots:
                for r in s.allowed_resources.all():
                    resource_set.add(r.resource_name)

            resource_string = ""
            for r in resource_set:
                resource_string += r + ", "
            resource_string = resource_string[:-2]

            context["table_rows"].append([m.machine_type_name, m.machine_category, len(m.machineslot_set.all()), len(m.machine_set.all()), resource_string])

    return render(request, 'machine_usage/forms/list_items.html', context)

@login_required
def list_resources(request):
    context = {
	    "table_headers":["Name", "Unit of Measure", "Cost per Unit", "In Stock?"],
	    "table_rows":[],
        "page_title":"Resources"
    }

    resources = Resource.objects.all()
    for r in resources:
	    context["table_rows"].append([r.resource_name, r.unit, r.cost_per, r.in_stock])

    return render(request, 'machine_usage/forms/list_items.html', context)

@login_required		
def list_users(request):
    context = {
        "table_headers":["Name", "RIN", "Outstanding Balance"],
        "table_rows":[],
        "page_title":"Users"
    }

    users = UserProfile.objects.all()
    for u in users:
        context["table_rows"].append([u.user.username, u.rin, format_usd(u.calculate_balance())])

    return render(request, 'machine_usage/forms/list_items.html', context)

def validate_slot_usage_list(slot_usage_list): # slot_usage_list has already been validated as a list.
    field_types = [("name", str), ("resource", str), ("quantity", str)]
    for slot_usage in slot_usage_list:
        for (name, expected_type) in field_types:
            if name not in slot_usage:
                return (False, f"Parameter {name} was not found in slot usage dictionary.")

            if not (type(slot_usage[name]) == expected_type):
                return (False, f"Parameter {name} was provided as type {type(slot_usage[name])} (expected {expected_type}).")

            try:
                dec = Decimal(slot_usage["quantity"])
            except Exception as e:
                return (False, f"Parameter quantity for slot {slot_usage['name']} was not a valid decimal number.")

    return (True, "")

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

def validate_machine(machine, slot_usages):
    input_set = set()
    model_set = set()

    for u in slot_usages:
        input_set.add(u["name"])

    model_names = machine.machine_type.get_slot_names()

    for n in model_names:
        model_set.add(n)

    return (input_set == model_set) and not machine.in_use

def validate_slot(slot, material, quantity):
    try:
        Decimal(quantity)
    except Exception as e:
        return False
    return slot.resource_allowed(material)

# $.post("http://localhost:8000/api/machines", '{"machine_name":"Prusa Alpha", "hours":1, "minutes":30,"slot_usages":[{"name":"Filament", "resource":"PLA", "quantity":10}]}')
@login_required
def create_machine_usage(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        machine_name = data["machine_name"]
        machine = Machine.objects.get(machine_name=machine_name)

        validation_result = validate_machine(machine, data["slot_usages"])

        if not validation_result:
            return HttpResponse("Invalid machine or schema.", status=400)

        slot_usages = []

        for slot_usage in data["slot_usages"]: # TODO Ensure that data["slot_usages"] is actually iterable. Or alternatively validate the JSON somewhere. List of dicts.
            slot_name = slot_usage["name"]
            resource = slot_usage["resource"]
            quantity = slot_usage["quantity"]

            slot = machine.machine_type.get_slot(slot_name)

            validation_result = validate_slot(slot, resource, quantity)
            if not validation_result:
                return HttpResponse(f"Quantity for slot {slot_name} was not a valid decimal, or the resource provided was invalid.", status=400)

            su = SlotUsage()
            slot_usages.append(su)
            su.machine_slot = slot
            su.resource = Resource.objects.get(resource_name=resource)
            su.amount = Decimal(quantity)

        u = Usage()
        u.machine = machine
        u.userprofile = request.user.userprofile
        u.save() # Necessary so start_time gets set to current time before referencing it below
        u.set_end_time(int(data["hours"]), int(data["minutes"]))
        u.save()

        for su in slot_usages:
            su.usage = u
            su.save()

        machine.in_use = True
        machine.current_job = u
        machine.save()

        return redirect('/')
    else:
        return HttpResponse("", status=405) # Method not allowed

# Login intentionally not required for create_user - new users should be able to create their own accounts.
def create_user(request):
    if request.method == 'POST':

        user_form = ForgeUserCreationForm(request.POST)
        profile_form = ForgeProfileCreationForm(request.POST)

        if(user_form.is_valid() and profile_form.is_valid()):
            # Save user and get values from user form
            user = user_form.save()

            user_rin = profile_form.cleaned_data.get('rin')
            user_gender = profile_form.cleaned_data.get('gender')
            user_major = profile_form.cleaned_data.get('major')
            
            # Update and save profile
            user.userprofile.rin = user_rin
            user.userprofile.gender = user_gender
            user.userprofile.major = user_major

            user.save()

            email = profile_form.cleaned_data.get('email')

            if not user.groups.filter(name="verified_email").exists():
                print(f"Sending verification email to {user.email}")
                utils.send_verification_email(user)

            login(request, user)
            return redirect('/myforge')
        else:
            return render(request, 'machine_usage/forms/create_user.html', {'user_form': user_form, 'profile_form': profile_form})
    else:
        user_form = ForgeUserCreationForm()
        profile_form = ForgeProfileCreationForm()

        return render(request, 'machine_usage/forms/create_user.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def volunteer_dashboard(request):
    return render(request, 'machine_usage/forms/volunteer_dashboard.html', {})

@login_required
def machine_usage(request):
    machines = Machine.objects.all()
    available_machines = {}

    for m in machines:
        if (not m.deleted) and (not m.in_use):
            type_name = m.machine_type.machine_type_name
            if type_name not in available_machines:
                available_machines[type_name] = []
            available_machines[type_name].append(m.machine_name)

    return render(request, 'machine_usage/forms/machine_usage.html', {"available_machines":available_machines})

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
        usage.clear_time = datetime.now()
        usage.complete = True
        usage.save()

        machine.current_job = None
        machine.in_use = False
        machine.save()
        return redirect('/forms/clear_machine')

#
#   API
#

@csrf_exempt # TODO REMOVE THIS, ONLY FOR DEBUG
def machine_endpoint(request):
    if request.method == 'GET':
        output = []

        machines = Machine.objects.all()

        for m in machines:
            if not m.deleted:
                machine_entry = {
                    "name": m.machine_name,
                    "in_use": m.in_use,
                    "enabled": m.enabled,
                    "status": m.status_message,
                    "usage_policy": m.machine_type.usage_policy,
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
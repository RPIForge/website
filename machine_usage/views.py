# Importing Django Utils
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models.base import ObjectDoesNotExist
from django.utils import timezone

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
from datetime import datetime, timedelta

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

def render_status(request):

    machines = Machine.objects.all().order_by('machine_name')
    output = []

    for m in machines:
        if m.in_use:
            u = m.current_job
            if u.failed:
                bar_type = "bar_failed"
                text_type = "text_failed"
            elif u.complete:
                bar_type = "bar_complete"
                text_type = "text_complete"
            elif u.error:
                bar_type = "bar_error"
                text_type = "text_error"
            else:
                bar_type = "bar_in_progress"
                text_type = "text_in_progress"

            if u.complete:
                bar_progress = 100
                time_remaining_text = "Time of Completion:"
                time_remaining = f""
                estimated_completion = u.end_time
            elif u.failed:

                fail_time = u.clear_time
                expiration_time = u.clear_time + timedelta(hours=1)

                percent_expired = (timezone.now() - fail_time).total_seconds() / (60 * 60)
                bar_progress = int(100 * percent_expired)

                time_remaining_text = "Restart By:"
                time_remaining = ""
                estimated_completion = u.clear_time + timedelta(hours=1)
            else:
                duration = u.end_time - u.start_time
                elapsed = timezone.now() - u.start_time
                percent_complete = elapsed.total_seconds() / duration.total_seconds()
                bar_progress = int(100 * percent_complete)

                time_remaining_text = "Estimated Completion:"
                time_remaining = f""
                estimated_completion = u.end_time

            output.append({
                "name": m.machine_name,
                "bar_type": bar_type,
                "text_type": text_type,
                "bar_progress":bar_progress,
                "type":m.machine_type.machine_type_name,
                "user":f"{m.current_job.userprofile.user.first_name} {m.current_job.userprofile.user.last_name[:1]}.",
                "status_message":m.current_job.status_message,
                "time_remaining_text": time_remaining_text,
                "estimated_completion": estimated_completion,
                "time_remaining": time_remaining
            })
        else:
            output.append({
                "name": m.machine_name,
                "bar_type": "bar_in_progress",
                "text_type": "text_in_progress",
                "bar_progress": 0,
                "type":m.machine_type.machine_type_name,
                "user":f"No User",
                "status_message":"Not In Use",
                "time_remaining_text": "",
                "estimated_completion": "",
                "time_remaining": ""
                })

    return render(request, 'machine_usage/status.html', {"machines":output})

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

    return render(request, 'machine_usage/forms/list_items_readonly.html', context)

@login_required
def list_machines(request):
    context = {
        "table_headers":["Name", "Category", "Type", "Status Message", "Enabled", "In Use?"],
        "table_rows":[],
        "page_title":"Machines",
        "edit_root":"machine_usage/machine"
    }

    machines = Machine.objects.all()
    for m in machines:
	    context["table_rows"].append({
            "row":[m.machine_name, m.machine_type.machine_category, m.machine_type.machine_type_name, m.status_message, m.enabled, m.in_use],
            "id":m.id
        })

    return render(request, 'machine_usage/forms/list_items.html', context)

@login_required
def list_machine_types(request):
    context = {
	    "table_headers":["Type", "Category", "Slots", "Count", "Resource Types"],
	    "table_rows":[],
        "page_title":"Machine Types",
        "edit_root":"machine_usage/machinetype"
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

            context["table_rows"].append({
                "row":[m.machine_type_name, m.machine_category, len(m.machineslot_set.all()), len(m.machine_set.all()), resource_string],
                "id":m.id
            })

    return render(request, 'machine_usage/forms/list_items.html', context)

@login_required
def list_resources(request):
    context = {
	    "table_headers":["Name", "Unit of Measure", "Cost per Unit", "In Stock?"],
	    "table_rows":[],
        "page_title":"Resources",
        "edit_root":"machine_usage/resource"
    }

    resources = Resource.objects.all()
    for r in resources:
	    context["table_rows"].append({
            "row":[r.resource_name, r.unit, r.cost_per, r.in_stock],
            "id":r.id
        })

    return render(request, 'machine_usage/forms/list_items.html', context)

@login_required		
def list_users(request):
    context = {
        "table_headers":["Name", "RIN", "Outstanding Balance"],
        "table_rows":[],
        "page_title":"Users",
        "edit_root":"auth/user"
    }

    users = UserProfile.objects.all()
    for u in users:
        context["table_rows"].append({
            "row":[u.user.username, u.rin, format_usd(u.calculate_balance())],
            "id":u.id
        })

    return render(request, 'machine_usage/forms/list_items.html', context)

@login_required     
def list_active_usages(request):
    context = {
        "table_headers":["User", "Machine Type", "Machine", "Cost", "Start Time", "Status Message"],
        "table_rows":[],
        "page_title":"Active Usages",
        "edit_root":"machine_usage/usage"
    }

    active_usages = Usage.objects.filter(complete=False)
    for u in active_usages:
        context["table_rows"].append({
            "row":[u.userprofile.user.username, u.machine.machine_type.machine_type_name, u.machine.machine_name, format_usd(u.cost()), u.start_time, u.status_message],
            "id":u.id
        })

    return render(request, 'machine_usage/forms/list_items.html', context)

@login_required     
def list_usages(request):
    context = {
        "table_headers":["User", "Machine Type", "Machine", "Cost", "Start Time", "End Time", "Clear Time", "Complete?", "Failed?", "Cost Overriden?", "Override Reason"],
        "table_rows":[],
        "page_title":"Usages",
        "edit_root":"machine_usage/usage"
    }

    usages = Usage.objects.all()
    for u in usages:
        context["table_rows"].append({
            "row":[u.userprofile.user.username, u.machine.machine_type.machine_type_name, u.machine.machine_name, format_usd(u.cost()), u.start_time, u.end_time, u.clear_time, u.complete, u.failed, u.cost_override, u.cost_override_reason],
            "id":u.id
        })

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

@login_required
def create_machine_usage(request):
    if request.method == 'POST':
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
        u.machine = machine
        u.userprofile = request.user.userprofile
        u.save() # Necessary so start_time gets set to current time before referencing it below
        u.set_end_time(int(data["hours"]), int(data["minutes"]))

        u.for_class = for_class
        u.own_material = own_material
        u.is_reprint = is_reprint

        u.save()

        for su in slot_usages:
            su.usage = u
            su.save()

        machine.in_use = True
        machine.current_job = u
        machine.save()

        return HttpResponse("Usage successfully recorded.", status=200)
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

# <div class="card">
#     <div class="loading_bar {{ machine.bar_type }}" data-value="{{ machine.bar_progress }}" data-machine-name="{{ machine.name }}"></div>
#     <div class="card_text {{machine.text_type}}">
#         <div class="machine_name">{{ machine.name }}</div>
#         <div class="user_name">{{ machine.type }} | {{ machine.user }}</div>
#         <div class="status_message">{{ machine.status_message }}</div>
#         <div class="time_remaining">{{machine.time_remaining_text}} <br />{{ machine.estimated_completion }}<br />{{ machine.time_remaining }}</div>
#     </div>
# </div>

@login_required
def volunteer_dashboard(request):

    machines = Machine.objects.all().order_by('machine_name')
    output = []

    for m in machines:
        if m.in_use:
            u = m.current_job
            if u.failed:
                bar_type = "bar_failed"
                text_type = "text_failed"
            elif u.complete:
                bar_type = "bar_complete"
                text_type = "text_complete"
            elif u.error:
                bar_type = "bar_error"
                text_type = "text_error"
            else:
                bar_type = "bar_in_progress"
                text_type = "text_in_progress"

            if u.complete:
                bar_progress = 100
                time_remaining_text = "Time of Completion:"
                time_remaining = f""
                estimated_completion = u.end_time
            elif u.failed:

                fail_time = u.clear_time
                expiration_time = u.clear_time + timedelta(hours=1)

                percent_expired = (timezone.now() - fail_time).total_seconds() / (60 * 60)
                bar_progress = int(100 * percent_expired)

                time_remaining_text = "Hold Until:"
                time_remaining = ""
                estimated_completion = u.clear_time + timedelta(hours=1)
            else:
                duration = u.end_time - u.start_time
                elapsed = timezone.now() - u.start_time
                percent_complete = elapsed.total_seconds() / duration.total_seconds()
                bar_progress = int(100 * percent_complete)

                time_remaining_text = "Estimated Completion:"
                time_remaining = f""
                estimated_completion = u.end_time

            output.append({
                "name": m.machine_name,
                "bar_type": bar_type,
                "text_type": text_type,
                "bar_progress":bar_progress,
                "type":m.machine_type.machine_type_name,
                "user":f"{m.current_job.userprofile.user.first_name} {m.current_job.userprofile.user.last_name[:1]}.",
                "status_message":m.current_job.status_message,
                "time_remaining_text": time_remaining_text,
                "estimated_completion": estimated_completion,
                "time_remaining": time_remaining
            })
        else:
            output.append({
                "name": m.machine_name,
                "bar_type": "bar_in_progress",
                "text_type": "text_in_progress",
                "bar_progress": 0,
                "type":m.machine_type.machine_type_name,
                "user":f"No User",
                "status_message":"Not In Use",
                "time_remaining_text": "",
                "estimated_completion": "",
                "time_remaining": ""
                })

    return render(request, 'machine_usage/forms/volunteer_dashboard.html', {"machines":output})

@login_required
def machine_usage(request):
    machines = Machine.objects.all().order_by("machine_name")
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
        usage.clear_time = timezone.now()
        usage.complete = True
        if (not usage.error) and (not usage.failed):
            usage.status_message = "Cleared."
        usage.save()

        machine.current_job = None
        machine.in_use = False
        machine.save()
        return redirect('/forms/clear_machine')

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
        machine_name = request.POST["machine_name"]
        machine = Machine.objects.get(machine_name=machine_name)

        usage = machine.current_job
        usage.clear_time = timezone.now()
        usage.failed = True
        usage.status_message = "Failed."
        usage.save()

        utils.send_failure_email(usage)
        return redirect('/forms/failed_usage')

#
#   API
#

@csrf_exempt # TODO REMOVE THIS, ONLY FOR DEBUG
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
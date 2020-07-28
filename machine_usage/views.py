# Importing Django Utils
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models.base import ObjectDoesNotExist
from django.utils import timezone

# Importing Models
from machine_management.models import *
from django.contrib.auth.models import User, Group

# Importing Other Libraries
import json
from datetime import datetime
from decimal import Decimal
from datetime import datetime, timedelta




@login_required
def render_unverified_email(request):
    if request.user.groups.filter(name="verified_email").exists():
        return redirect('/myforge')
    return render(request, 'machine_usage/unverified_email.html', {})

@login_required
def render_begin_semester(request):
    if request.method == "GET":
        if request.user.userprofile.is_active:
            return redirect('/myforge')
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




@login_required # TODO restrict permissions
def render_force_email_verification(request):
    if request.method == "GET":
        return render(request, "machine_usage/forms/force_email_verification.html", {})
    elif request.method == "POST":
        group = Group.objects.get(name="verified_email") # TODO Create this group if it doesn't exist - current solution is to add the group manually from the admin panel.
        user = User.objects.get(username=request.POST["rcs_id"])
        user.groups.add(group)
        user.save()
        return redirect('/forms/force_email_verification')



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
def machine_usage(request):
    machines = Machine.objects.all().filter(deleted=False, in_use=False, enabled=True).order_by("machine_name")
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

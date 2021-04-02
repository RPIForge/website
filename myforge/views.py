 # Importing Django Utils
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings

# Importing Models
from django.contrib.auth.models import User, Group

from machine_management.models import *
from machine_management.forms import *


# Importing Other Libraries
import json
from datetime import datetime
from decimal import Decimal
from datetime import datetime, timedelta



#
#   General MyForge Functions
#

# ! type: GET
# ! function: Generate the my forge frame
# ? required: None
# ? returns: HTTP Rendered Template
# TODO:
@login_required
def render_myforge(request):
    if(not request.user.groups.filter(name = "member").exists()):
        return redirect('/begin_semester')

    if not request.user.groups.filter(name="verified_email").exists():
        return redirect('/unverified_email')

    return render(request, 'myforge/myforge.html', {})

# ! type: Helper function
# ! function: Get the current chat url
# ? required: path of chat
# ? returns: url as a String
# TODO:
def get_chat_url(request, path):
    if request.is_secure():
        url="https://"+settings.CHAT_SITE_URL+":443"+path
    else:
        url="http://"+settings.CHAT_SITE_URL+":"+str(settings.CHAT_SITE_PORT)+path

    if request.user.is_authenticated:
        url=url+"?uuid={}".format(request.user.userprofile.uuid)
        url=url+"&name={}".format(request.user.get_full_name())
        url=url+"&email={}".format(request.user.email)
    return url




#
#   Chat Functions
#

# ! type: GET
# ! function: Generate link to iframe 
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: Move to main
def user_chat(request):
    url = get_chat_url(request, '/user/info') 
    return render(request, 'myforge/forms/user_chat_template.html', {'channels_link':url})

# ! type: GET
# ! function: Generate link to iframe 
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: Move to main
@login_required
def volunteer_chat_join(request):
    url = get_chat_url(request, '/volunteer/select')
    return redirect(url)

# ! type: GET
# ! function: Generate link to iframe 
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: Move to main
@login_required
def user_chat_history(request):
    url = get_chat_url(request, '/user/history/select')
    return redirect(url)
    
# ! type: GET
# ! function: Generate link to iframe 
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: Move to main
@login_required
def manager_chat_history(request):
    url = get_chat_url(request, "/manager/history/select")
    return redirect(url)

# ! type: GET
# ! function: Generate link to iframe 
# ? required: None
# ? returns: HTTP Rendered Template  
# TODO: Move to main
@login_required
def manager_chat_requests(request):
    url = get_chat_url(request, "/manager/request/select")
    return redirect(url)


#
#   Buisness
#

# ! type: GET
# ! function: Generate form to download charge sheets
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
@login_required
def render_charge_sheet(request):
    semester = Semester.objects.all().order_by("-current")
    semester_list = []
    for item in semester:
        semester_list.append({'id': item.id, 'name': str(item)})
    
    return render(request, 'myforge/forms/charge_sheet.html', {'semester_list':semester_list})
    

# ! type: GET
# ! function: Generate form to create semesters
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
@login_required
def render_change_semesters(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        semester_form = SemesterCreationForm(request.POST)
        # check whether it's valid:
        if semester_form.is_valid():
            # process the data in form.cleaned_data as required
            semester = semester_form.save()
            
            members = Group.objects.get(name='member') 
            volunteers = Group.objects.get(name='volunteers') 
            managers = Group.objects.get(name='managers') 
            admins = Group.objects.get(name='admins') 
            
            #clear members, volunteers, managers
            members.user_set.clear()
            volunteers.user_set.clear()
            managers.user_set.clear()
            
            for user in admins.user_set.all():
               user.groups.add(members, managers, volunteers)
                
                
            # redirect to a new URL:
            return render(request, 'myforge/forms/change_semester.html', {'submit': True}) 

    
    
# ! type: Helper Function
# ! function: Format cost
# ? required: Cost as float
# ? returns: Formated cost as string
# TODO: 
def format_usd(fp):
    return f"${fp:.2f}"

# ! type: GET
# ! function: Generate table for projects
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: Display this on a template that doesn't show actions - e.g. is read-only.
@login_required
def list_projects(request):
    #
    
    
    user_profile = request.user.userprofile

    context = {
        "table_headers":["Semester","Date", "Machine", "Cost"],
        "table_rows":[],
        "page_title":"Projects"
    }

    usages = user_profile.usage_set.all()
    for u in usages:
        context["table_rows"].append([u.semester, u.start_time, u.machine.machine_name, format_usd(u.cost())])

    return render(request, 'myforge/forms/list_items_readonly.html', context)

# ! type: GET
# ! function: Generate table of machines
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
@login_required
def list_machines(request):
    context = {
        "table_headers":["Name", "Category", "Type", "Status Message", "Enabled", "Time Used", "In Use?"],
        "table_rows":[],
        "page_title":"Machines",
        "edit_root":"machine_management/machine"
    }

    machines = Machine.objects.all()
    for m in machines:
	    context["table_rows"].append({
            "row":[m.machine_name, m.machine_type.machine_category, m.machine_type.machine_type_name, m.status_message, m.enabled, m.time_used(), m.in_use],
            "id":m.id
        })

    return render(request, 'myforge/forms/list_items.html', context)

# ! type: GET
# ! function: Generate table of machine types
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
@login_required
def list_machine_types(request):
    context = {
	    "table_headers":["Type", "Category", "Hourly Cost", "Slots", "Count", "Resource Types"],
	    "table_rows":[],
        "page_title":"Machine Types",
        "edit_root":"machine_management/machinetype"
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
                "row":[m.machine_type_name, m.machine_category, format_usd(m.hourly_cost), len(m.machineslot_set.all()), len(m.machine_set.all()), resource_string],
                "id":m.id
            })

    return render(request, 'myforge/forms/list_items.html', context)

# ! type: GET
# ! function: Generate table of resources
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
@login_required
def list_resources(request):
    context = {
	    "table_headers":["Name", "Unit of Measure", "Cost per Unit", "Units Used", "In Stock?"],
	    "table_rows":[],
        "page_title":"Resources",
        "edit_root":"machine_management/resource"
    }

    resources = Resource.objects.all()
    for r in resources:
	    context["table_rows"].append({
            "row":[r.resource_name, r.unit, format_usd(r.cost_per), f"{r.units_used():.2f} {r.unit}", r.in_stock],
            "id":r.id
        })

    return render(request, 'myforge/forms/list_items.html', context)

# ! type: GET
# ! function: Generate table of users
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
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
        if(u.user.groups.filter(name = "member").exists()):
        
            context["table_rows"].append({
                "row":[u.user.username, u.rin, format_usd(u.calculate_balance())],
                "id":u.user.id
            })

    return render(request, 'myforge/forms/list_items.html', context)

# ! type: GET
# ! function: Generate table of active usages
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
@login_required     
def list_active_usages(request):
    context = {
        "table_headers":["User", "Machine Type", "Machine", "Cost", "Start Time", "Status Message"],
        "table_rows":[],
        "page_title":"Active Usages",
        "edit_root":"machine_management/usage"
    }

    active_usages = Usage.objects.filter(complete=False)
    for u in active_usages:
        context["table_rows"].append({
            "row":[u.userprofile.user.username, u.machine.machine_type.machine_type_name, u.machine.machine_name, format_usd(u.cost()), u.start_time, u.status_message],
            "id":u.id
        })

    return render(request, 'myforge/forms/list_items.html', context)

# ! type: GET
# ! function: Generate table of all usages this semester
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
@login_required     
def list_usages(request):
    context = {
        "table_headers":["Semester", "User", "Machine Type", "Machine", "Cost", "Start Time", "End Time", "Clear Time", "Complete?", "Failed?", "Cost Overriden?", "Override Reason"],
        "table_rows":[],
        "page_title":"Usages",
        "edit_root":"machine_management/usage"
    }

    usages = Usage.objects.all()
    for u in usages:
        if(u.semester.current):
            context["table_rows"].append({
                "row":[u.semester, u.userprofile.user.username, u.machine.machine_type.machine_type_name, u.machine.machine_name, format_usd(u.cost()), u.start_time, u.end_time, u.clear_time, u.complete, u.failed, u.cost_override, u.cost_override_reason],
                "id":u.id
            })

    return render(request, 'myforge/forms/list_items.html', context)

# ! type: Helper Function
# ! function: Generate table of machines
# ? required: None
# ? returns: Tuple of success boolean and error message
# TODO: 
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
    
    
    
# ! type: GET
# ! function: Generate volunteer dashboad
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
@login_required
def volunteer_dashboard(request):

    machines = Machine.objects.filter(enabled=True).order_by('machine_name')
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
                "id": m.id,
                "name": m.machine_name,
                "bar_type": bar_type,
                "text_type": text_type,
                "bar_progress": bar_progress,
                "type": m.machine_type.machine_type_name,
                "user": f"{m.current_job.userprofile.user.first_name} {m.current_job.userprofile.user.last_name[:1]}.",
                "status_message":m.current_job.status_message,
                "time_remaining_text": time_remaining_text,
                "estimated_completion": estimated_completion,
                "time_remaining": time_remaining,
                "current_usage_id": m.current_job.id,
                "in_use": True
            })
        else:
            output.append({
                "id": m.id,
                "name": m.machine_name,
                "bar_type": "bar_in_progress",
                "text_type": "text_in_progress",
                "bar_progress": 0,
                "type": m.machine_type.machine_type_name,
                "user": f"No User",
                "status_message": "Not In Use",
                "time_remaining_text": "",
                "estimated_completion": "",
                "time_remaining": "",
                "current_usage_id": "",
                "in_use": False
                })

    return render(request, 'myforge/forms/volunteer_dashboard.html', {"machines":output})

# Importing Django stuff
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models.base import ObjectDoesNotExist

from machine_usage.models import *

#
#	Pages/Login
#

def render_index(request):
    return render(request, 'machine_usage/index.html', {})
# Importing Models
from django.contrib.auth.models import User, Group


def render_equipment(request):
    return render(request, 'machine_usage/equipment.html', {})

def render_hours(request):
    return render(request, 'machine_usage/index.html', {}) # TO-DO: Implement the "Hours" page.

def render_index(request):
    return render(request, 'machine_usage/index.html', {})

def render_login(request):
    if request.method == 'GET':

        if request.user.is_authenticated:
            return redirect('/machine_usage/myforge')
        else:
            return render(request, 'machine_usage/login.html', {})

    elif request.method == 'POST':

        rcs_id = request.POST['rcsid']
        password = request.POST['password']

        user = authenticate(request, username=rcs_id, password=password)

        if user is not None:
            login(request, user)
            return redirect('/machine_usage/myforge')
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
    return render(request, 'machine_usage/myforge.html', {})

def log_out(request):
    logout(request)
    return redirect('/machine_usage/')


#
#	Forms/Tables
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
	    "table_rows":[]
    }

    usages = user_profile.usage_set.all()
    for u in usages:
	    context["table_rows"].append([u.start_time, u.machine.machine_name, format_usd(u.cost())])

    return render(request, 'machine_usage/forms/list_items.html', context)

@login_required
def list_machines(request):
    context = {
	    "table_headers":["Name", "Category", "Type", "Status Message", "Enabled", "In Use?"],
	    "table_rows":[]
    }

    machines = Machine.objects.all()
    for m in machines:
	    context["table_rows"].append([m.machine_name, m.machine_type.machine_category, m.machine_type.machine_type_name, m.status_message, m.enabled, m.in_use])

    return render(request, 'machine_usage/forms/list_items.html', context)

@login_required
def list_machine_types(request):
    context = {
	    "table_headers":["Type", "Category", "Slots", "Count", "Resource Types"],
	    "table_rows":[]
    }

    machine_types = MachineType.objects.all()
    for m in machine_types:

            slots = m.machineslot_set.all()
            resource_set = set()

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
	    "table_rows":[]
    }

    resources = Resource.objects.all()
    for r in resources:
	    context["table_rows"].append([r.resource_name, r.unit, r.cost_per, r.in_stock])

    return render(request, 'machine_usage/forms/list_items.html', context)

@login_required		
def list_users(request):
    context = {
	    "table_headers":["Name", "RIN", "Outstanding Balance"],
	    "table_rows":[]
    }

    users = UserProfile.objects.all()
    for u in users:
	    context["table_rows"].append([u.user.username, u.rin, format_usd(u.calculate_balance())])

    return render(request, 'machine_usage/forms/list_items.html', context)

@login_required
def volunteer_dashboard(request):
    return render(request, 'machine_usage/forms/volunteer_dashboard.html', {})

 # Importing Django Utils
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings

# Importing Models
from organization_management.models import *

# Importing Other Libraries



#
#  MyForge Organization
#

# ! type: GET
# ! function: Generate join organization list
# ? required: None
# ? returns: HTTP Rendered Template
# TODO:
@login_required
def list_joinable_organizations(request):
    user = request.user

    org_list = Organization.objects.filter(visible=True).exclude(memberships__user=user)

    context = {
        "table_headers":["Name", "Description", "Membership Cost"],
        "table_rows":[],
        "page_title":"Organizations",
        "org_ids": {}
    }

    for org in org_list:
        context["table_rows"].append([org.name, org.description, org.pretty_print_membership_fee()])
        context['org_ids'][org.name]=org.org_id


    return render(request, 'organization_management/forms/list_joinable_organizations.html', context)
    
# ! type: GET
# ! function: Generate table for organziation projects
# ? required: None
# ? returns: HTTP Rendered Template
@login_required
def list_oragnization_projects(request):
    user = request.user
    user_profile = user.userprofile

    context = {
        "table_headers":["Semester","Date", "Machine", "Cost"],
        "table_rows":[],
        "page_title":"Projects"
    }

    usages = user_profile.usage_set.all()
    for u in usages:
        context["table_rows"].append([u.semester, u.start_time, u.machine.machine_name, format_usd(u.cost())])

    return render(request, 'myforge/forms/list_items_readonly.html', context)

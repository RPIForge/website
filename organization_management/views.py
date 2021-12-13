 # Importing Django Utils
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings

# Importing Models
from organization_management.models import *
from machine_management.models import *

# Importing Other Libraries



#
#  MyForge Organization
#



# ! type: GET
# ! function: View list of users organizations
# ? required: None
# ? returns: HTTP Rendered Template
# TODO:

@login_required
def user_list_organizations(request):
    context = {
        "table_headers":["Organization", "Description", "Access", "Membership Fee"],
        "table_rows":[],
        "page_title":"Joined Organization",
    }

    user = request.user
    userprofile = user.userprofile

    for org in userprofile.get_organizations():
	    context["table_rows"].append([org.name, org.description, org.access, org.membership_fee])

    return render(request, 'myforge/forms/list_items_readonly.html', context)

# ! type: GET
# ! function: View list of Organization Memberships
# ? required: None
# ? returns: HTTP Rendered Template
# TODO:
@login_required
def list_organization_membership(request):
    user = request.user

    org_list = Organization.objects.filter(memberships__user=user,memberships__manager=True)

    context = {
        "table_headers":["Name","Number of Projects","Total Expense"],
        "org_data":{},
        "org_ids": {},
        "page_title":"Organization Memberships"
    }

    for org in org_list:
        context['org_ids'][org.name]=org.org_id
        context['org_data'][org.name]=[]
        for user in org.get_users():
            userprofile = user.userprofile
            
            
            usage_list = org.get_current_usages(user)
            total_cost = 0
            for usage in usage_list:
                total_cost = total_cost + float(usage.cost())
            
            usage_count = usage_list.count()

            context['org_data'][org.name].append([user.get_full_name(),usage_count,"%.2f" % total_cost])

    return render(request, 'organization_management/list_organization_membership.html', context)

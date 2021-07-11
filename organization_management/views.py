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
    print(context)
    return render(request, 'organization_management/forms/list_joinable_organizations.html', context)

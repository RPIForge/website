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
        "table_headers":["Name", "Description", "Membership Cost", "Action"],
        "table_rows":[],
        "page_title":"Organizations"
    }

    for org in org_list:
        context["table_rows"].append([org.name, org.description, org.membership_fee, "<button>Test</button>"])


    return render(request, 'myforge/forms/list_items_readonly.html', context)

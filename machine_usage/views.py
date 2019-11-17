# Importing Django stuff
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models.base import ObjectDoesNotExist

# Importing Models
from django.contrib.auth.models import User, Group
from machine_usage.models import UserProfile


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
    return render(request, 'machine_usage/index.html', {}) # TO-DO: Implement the "News" page.

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


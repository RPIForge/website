#import django methods
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group

#import database tables
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
    #output dictionary
    verification_dict = {"already_verified":False,"email_verified":False}
    
    #if method is correct type
    if request.method == 'GET':
        #get email id from request
        token = request.GET.get("user_token",'')
        
        #if no email id paramaters redirect to error
        if(token == ''):
            print("Failed 1")
            return render(request, 'machine_usage/verify_email.html', verification_dict)
            
        #try getting the user that corispondes to the token
        try:
            #get user id from user profile which is from token
            user_profile = UserProfile.objects.get(user_token=token)
            user_id = user_profile.user_id
            #get the user and group objects
            user = User.objects.get(id=user_id)
            group = Group.objects.get(name="Verified_Email")
            
            #if user is in group then return already verified
            if(user.groups.filter(name="Verified_Email")):
                verification_dict["already_verified"] = True
                verification_dict["email_verified"] = True            
            else:
                #add user to email group
                user.groups.add(group)
                user.save()
                verification_dict["email_verified"] = True
        except:
            verification_dict["email_verified"] = False
            return render(request, 'machine_usage/verify_email.html',verification_dict)
    return render(request, 'machine_usage/verify_email.html',verification_dict) 
         
       
@login_required
def render_myforge(request):
    return render(request, 'machine_usage/myforge.html', {})

def log_out(request):
    logout(request)
    return redirect('/machine_usage/')


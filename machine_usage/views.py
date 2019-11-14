from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
    #if method is correct type
    if request.method == 'GET':
        #get email id from request
        email_token = request.GET.get("email_token",'')
        
        #if no email id paramaters redirect to error
        if(email_token == ''):
            print("failed 1")
        
        #try getting the user that corispondes to the token
        try:
            user = UserProfile.objects.get(verification_token=email_token)
            print(user)
        except:
            print("failed 2")

    return redirect('/machine_usage/') 
         
       
@login_required
def render_myforge(request):
    return render(request, 'machine_usage/myforge.html', {})

def log_out(request):
    logout(request)
    return redirect('/machine_usage/')
    

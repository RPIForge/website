from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def render_index(request):
    return render(request, 'machine_usage/index.html', {})

def render_our_space(request):
    return render(request, 'machine_usage/index.html', {})

def render_equipment(request):
    return render(request, 'machine_usage/equipment.html', {})

def render_status(request):
    return render(request, 'machine_usage/index.html', {})

def render_news(request):
    return render(request, 'machine_usage/index.html', {})

def render_hours(request):
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
        

def render_myforge(request):
    if request.user.is_authenticated:
        return render(request, 'machine_usage/myforge.html', {})
    else:
        return redirect('/machine_usage/login')

def log_out(request):
    logout(request)
    return redirect('/machine_usage/')
    

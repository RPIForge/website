# Importing Django Utils
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Importing Models

from user_management.models import *
from django.contrib.auth.models import User, Group

# Importing Forms
from user_management.forms import ForgeUserCreationForm, ForgeProfileCreationForm

# Importing Helper Functions
import forge.utils as utils





@login_required
def render_begin_semester(request):
    if request.method == "GET":
        if request.user.groups.filter(name = "member").exists():
            return redirect('/myforge')
        return render(request, 'user_management/begin_semester.html', {})
    elif request.method == "POST":
        profile = request.user.userprofile

        if request.POST["accepts_charges"] == "yes":
            profile.is_active = True
        else:
            profile.is_active = False

        if request.POST["is_graduating"] == "yes":
            profile.is_graduating = True
        else:
            profile.is_graduating = False

        profile.save()
        
        member_group, created = Group.objects.get_or_create(name='member')
        member_group.user_set.add(request.user)
        return redirect('/myforge')




@login_required # TODO restrict permissions
def render_force_email_verification(request):
    if request.method == "GET":
        return render(request, "user_management/forms/force_email_verification.html", {'outcome':'none'})
    elif request.method == "POST":
        group = Group.objects.get_or_create(name="verified_email") 
        try:
            user = User.objects.get(username=request.POST["rcs_id"])
        except User.DoesNotExist:
        
            return render(request, "user_management/forms/force_email_verification.html", {'outcome':'failure'})
       
        user.groups.add(group)
        user.save()
        
        return render(request, "user_management/forms/force_email_verification.html", {'outcome':'success'})



@login_required
def render_unverified_email(request):
    if request.user.groups.filter(name="verified_email").exists():
        return redirect('/myforge')
    return render(request, 'user_management/unverified_email.html', {})



#render login 
def render_login(request):
    if request.method == 'GET':

        if request.user.is_authenticated:
            return redirect('/myforge')
        else:
            return render(request, 'user_management/login.html', {})

    elif request.method == 'POST':

        rcs_id = request.POST['rcsid'].lower()
        password = request.POST['password']

        user = authenticate(request, username=rcs_id, password=password)

        if user is not None:
            player, created = UserProfile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('/myforge')
        else:
            return render(request, 'user_management/login.html', {"error":"Login failed."})

#log user out
def log_out(request):
    logout(request)
    return redirect('/')
    
    
# Login intentionally not required for create_user - new users should be able to create their own accounts.
def create_user(request):
    if request.method == 'POST':
        user_form = ForgeUserCreationForm(request.POST)
        profile_form = ForgeProfileCreationForm(request.POST)

        if(user_form.is_valid() and profile_form.is_valid()):
            # Save user and get values from user form
            user = user_form.save()

            user_rin = profile_form.cleaned_data.get('rin')
            user_gender = profile_form.cleaned_data.get('gender')
            user_major = profile_form.cleaned_data.get('major')

            # Update and save profile
            user.userprofile.rin = user_rin
            user.userprofile.gender = user_gender
            user.userprofile.major = user_major

            user.username = user.username.lower()

            if ("is_graduating" in request.POST) and (request.POST["is_graduating"] == "on"):
                user.userprofile.is_graduating = True
            else:
                user.userprofile.is_graduating = False

            if ("accepts_charges" in request.POST) and (request.POST["accepts_charges"] == "on"):
                user.userprofile.is_active = True
            else:
                user.userprofile.is_active = False

            user.save()

            email = profile_form.cleaned_data.get('email')

            if not user.groups.filter(name="verified_email").exists():
                print(f"Sending verification email to {user.email}")
                utils.send_verification_email(user)

            login(request, user)
            return redirect('/myforge')
        else:
            return render(request, 'user_management/forms/create_user.html', {'user_form': user_form, 'profile_form': profile_form})
    else:
        user_form = ForgeUserCreationForm()
        profile_form = ForgeProfileCreationForm()

        return render(request, 'user_management/forms/create_user.html', {'user_form': user_form, 'profile_form': profile_form})

#verify email
def render_verify_email(request):
    # Make sure we only support GET requests, so we can make POST do something later if needed
    if request.method == 'GET':
        # Get the verification token from the request, or a NoneType if the request is malformed.
        token = request.GET.get("token", None)

        if token is None:
            return render(request, 'user_management/verify_email.html', {"has_message":True, "message_type":"error", "message":"Invalid Request: No token provided."})

        # See if we have a user that corresponds to the token.
        try:
            user_profile = UserProfile.objects.get(email_verification_token=token)
        except ObjectDoesNotExist:
            return render(request, 'user_management/verify_email.html', {"has_message":True, "message_type":"error", "message":"Invalid Token."})

        user = user_profile.user

        if(user.groups.filter(name="verified_email")):
            return render(request, 'user_management/verify_email.html', {"has_message":True, "message_type":"info", "message":"Email already verified."})
        else:
            group = Group.objects.get(name="verified_email") # TODO Create this group if it doesn't exist - current solution is to add the group manually from the admin panel.
            user.groups.add(group)
            user.save()
            return render(request, 'user_management/verify_email.html', {"has_message":True, "message_type":"success", "message":"Successfully verified email!"})




@login_required
def resend_email_verification(request):
    if not request.user.groups.filter(name="verified_email").exists():
        print(f"Sending verification email to {request.user.email}")
        utils.send_verification_email(request.user)
    return redirect('/myforge')
    
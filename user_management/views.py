# Importing Django Utils
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict

# Importing Models

from user_management.models import *
from django.contrib.auth.models import User, Group

# Importing Forms
from user_management.forms import ForgeUserCreationForm, ForgeProfileCreationForm

# Importing Helper Functions
import forge.utils as utils




# ! type: GET/POST
# ! function: Render begin semester form to update user profile
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
@login_required
def render_begin_semester(request):
    if request.method == "GET":
        if request.user.groups.filter(name = "member").exists():
            return redirect('/myforge')
        return render(request, 'user_management/begin_semester.html', {})
    elif request.method == "POST":
        profile = request.user.userprofile

        member_group, created = Group.objects.get_or_create(name='member')
        member_group.user_set.add(request.user)

        if request.POST.get("is_graduating","") == "yes":
            profile.is_graduating = True
        else:
            profile.is_graduating = False
        
        profile.save()
        
        
        return redirect('/myforge')



# ! type: GET/POST
# ! function: Force user email verification
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
@login_required # TODO restrict permissions
def render_force_email_verification(request):
    if request.method == "GET":
        return render(request, "user_management/forms/force_email_verification.html", {'outcome':'none'})
    elif request.method == "POST":
        group = Group.objects.get_or_create(name="verified_email")[0]
        try:
            user = User.objects.get(username=request.POST.get("rcs_id",""))
        except User.DoesNotExist:
        
            return render(request, "user_management/forms/force_email_verification.html", {'outcome':'failure'})
        

        group.user_set.add(user)

        return render(request, "user_management/forms/force_email_verification.html", {'outcome':'success'})


# ! type: GET
# ! function: Render unverified email page
# ? required: None
# ? returns: HTTP Rendered Template
# TODO: 
@login_required
def render_unverified_email(request):
    if request.user.groups.filter(name="verified_email").exists():
        return redirect('/myforge')
    return render(request, 'user_management/unverified_email.html', {})



# ! type: GET/POST
# ! function: Render user login page
# ? required: None/Login information
# ? returns:  HTTP Rendered Template/Redirect
# TODO: 
def render_login(request):
    if request.method == 'GET':
        token = request.GET.get("token", None)
        user_profile = UserProfile.objects.filter(email_verification_token=token).first()
        if(user_profile is not None):
            user = userprofile.user

            #verify user email if not already
            group = Group.objects.get_or_create(name="verified_email") 
            group.user_set.add(user)
            group.save()


            login(request, user)
            return redirect('/myforge')

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

# ! type: GET
# ! function: Log out the selected user
# ? required: None
# ? returns: redirect
# TODO: 
#log user out
def log_out(request):
    logout(request)
    return redirect('/')
    
    

# ! type: GET/POST
# ! function: Render user creation form/Create user 
# ? required: None/Form data
# ? returns: HTTP Rendered Template/rediect
# TODO: 
def create_user(request):
    if request.method == 'POST':
        user = None
        userprofile = None
        if not request.user.is_anonymous:
            user = request.user
            userprofile = user.userprofile

        user_form = ForgeUserCreationForm(request.POST, created=user is not None, instance=user)
        profile_form = ForgeProfileCreationForm(request.POST, instance=userprofile)

        if(user_form.is_valid() and profile_form.is_valid()):
            # Save user and get values from user form
            user_form.save()
            user.userprofile = profile_form.save()
            user.userprofile.is_active = True
            user.userprofile.save()
            
            if not user.groups.filter(name="verified_email").exists():
                print(f"Sending verification email to {user.email}")
                utils.send_verification_email(user)

            login(request, user)
            return redirect('/myforge')
        else:
            if(user and 'username' in user_form.fields):
                user_form.fields['username'].disabled = True

            if(user and 'email' in user_form.fields):
                user_form.fields['email'].disabled = True

            return render(request, 'user_management/forms/create_user.html', {'user_form': user_form, 'profile_form': profile_form})
    else:
        user = None
        userprofile = None
        initial_data = {}
        if(not request.user.is_anonymous):
            user = request.user
            userprofile = user.userprofile
            initial_data = model_to_dict(user)


        user_form = ForgeUserCreationForm(created=user is not None,instance=user, initial=initial_data)
        profile_form = ForgeProfileCreationForm(instance=userprofile)

        return render(request, 'user_management/forms/create_user.html', {'user_form': user_form, 'profile_form': profile_form})



# ! type: GET
# ! function: Verify users email
# ? required: email token
# ? returns: HTTP Rendered Template
# TODO: 
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
            group, created = Group.objects.get_or_create(name="verified_email") 
            
            group.user_set.add(user)
            group.save()
            return render(request, 'user_management/verify_email.html', {"has_message":True, "message_type":"success", "message":"Successfully verified email!"})



# ! type: GET
# ! function: Resend verification email
# ? required: None
# ? returns: redirect
# TODO: 
@login_required
def resend_email_verification(request):
    if not request.user.groups.filter(name="verified_email").exists():
        print(f"Sending verification email to {request.user.email}")
        utils.send_verification_email(request.user)
    return redirect('/myforge')
    

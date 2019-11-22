#django imports
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

#class import
import machine_usage.lists
from machine_usage.models import UserProfile


class ForgeUserCreationForm(UserCreationForm):
    user = forms.CharField(max_length=30)
    rin = forms.CharField()
    gender = forms.Select(choices=machine_usage.lists.gender)
    major = forms.Select(choices=machine_usage.lists.major)
    
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = UserProfile 
        fields = ('user', 'first_name', 'last_name','rin','gender','major','email', 'password1', 'password2', )

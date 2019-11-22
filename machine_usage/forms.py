#django imports
from django import forms
from django.contrib.auth.models import User

#class import
import machine_usage.lists
from machine_usage.models import UserProfile

class ForgeUserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password',widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password',widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

class ForgeProfileCreationForm(forms.ModelForm):
    rin = forms.CharField()
    gender = forms.Select(choices=machine_usage.lists.gender)
    major = forms.Select(choices=machine_usage.lists.major)
    
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = UserProfile 
        fields = ('rin','gender','major')

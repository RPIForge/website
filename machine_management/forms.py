#django imports
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models.base import ObjectDoesNotExist 

#class import
from machine_management.models import *

class SemesterCreationForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(SemesterCreationForm, self).__init__(*args, **kwargs)

    class Meta:                                 
        model = Semester 
        fields = ('year','season')
        widgets = {
            'year': forms.TextInput(attrs={'placeholder': '2021'}),
            'season': forms.TextInput(attrs={'placeholder': 'Fall'}),
        }

#django imports
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models.base import ObjectDoesNotExist 

#class import
import machine_usage.lists
from machine_usage.models import UserProfile

class ForgeUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(ForgeUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    def clean(self, *args, **kwargs):
        super(ForgeUserCreationForm , self).clean(*args, **kwargs)
        
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')

        if email  and User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Email addresses must be unique.',code='duplicate_email')
        
        
        
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        help_texts = {
            'username': None,
            'email': None,
        }


class ForgeProfileCreationForm(forms.ModelForm):
    rin = forms.CharField()
    gender = forms.Select(choices=machine_usage.lists.gender)
    major = forms.Select(choices=machine_usage.lists.major)
    
    
    def __init__(self, *args, **kwargs):
        super(ForgeProfileCreationForm, self).__init__(*args, **kwargs)
        
        self.fields['rin'].required = True
        self.fields['gender'].required = True
        self.fields['major'].required = True
   
    def clean(self, *args , **kwargs):
        super(ForgeProfileCreationForm, self).clean(*args ,**kwargs) 
        
        rin = self.cleaned_data['rin']

        if(rin):
            #See if rin is an integer                                                    
            try:
                int(rin)
            except ValueError:
                raise forms.ValidationError("Invalid Rin", code='invalid_rin')
            
            #See if rin is correct length
            if(len(rin) != 9):
                raise forms.ValidationError("Invalid Rin", code='invalid_rin')

            #See if rin already exists
            try:
                UserProfile.objects.get(rin=self.cleaned_data['rin'])
                raise forms.ValidationError("Rin already taken", code='duplicate_rin')
            except ObjectDoesNotExist:
                pass

            
        return self.cleaned_data
    
    class Meta:                                 
        model = UserProfile 
        fields = ('rin','gender','major')

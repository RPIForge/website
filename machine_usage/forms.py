#django imports
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


#class import
import machine_usage.lists
from machine_usage.models import UserProfile

class ForgeUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(ForgeUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

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
        
    class Meta:
        model = UserProfile 
        fields = ('rin','gender','major')
    def clean(self, *args , **kwargs):
        super(ForgeProfileCreationForm, self).clean(*args ,**kwargs) 
        
        if( 'rin' in self.cleaned_data):
            if(len(self.cleaned_data['rin']) != 9):
                raise forms.ValidationError("Invalid Rin")

            try:
                int(self.cleaned_data['rin'])
            except:
                raise forms.ValidationError("Invalid Rin")

        return self.cleaned_data
        

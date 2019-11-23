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
        fields = ('username', 'first_name', 'last_name', 'email')

class ForgeProfileCreationForm(forms.ModelForm):
    rin = forms.CharField()
    gender = forms.Select(choices=machine_usage.lists.gender)
    major = forms.Select(choices=machine_usage.lists.major)
    

    class Meta:
        model = UserProfile 
        fields = ('rin','gender','major')

    def clear(self):
        rin = self.cleaned_data.get("rin")
        
        if(len(rin)!=9):
            raise ValidationError("Invalid Rin")

        try:
            int(rin)
        except:
            raise ValidationError("Invlaid Rin")
    
        
    
    def is_valid(self):
        # run the parent validation first
        valid = super(ForgeProfileCreationForm, self).is_valid()
        
        # we're done now if not valid
        if not valid:
            return valid

        rin = self.cleaned_data['rin'].strip()

        if(len(rin)!=9):
           valid = False

        try:
            int(rin)
        except:
            valid = False

        if not valid:
            self._errors['invalid_rin'] = 'Invlaid Rin'
            return valid

        try:
            user = UserProfile.objects.get(rin=rin)
            valid = False
            self._errors['exists_rin'] = 'Rin already exists'
            return valid
        except:
            pass

        return True

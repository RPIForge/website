#django imports
from django import forms
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models.base import ObjectDoesNotExist 
from django.shortcuts import render


#class import
from organization_management.models import *
from user_management.models import UserProfile

#custom imports
from formtools.wizard.views import SessionWizardView



class OrganizationListForm(forms.Form):
    org_id = forms.CharField(max_length=8,required=False)

    org_count = 0

    def clean(self, *args , **kwargs):
        super(OrganizationListForm, self).clean(*args ,**kwargs) 

        org_id = self.cleaned_data['org_id']
        if(org_id==''):
            return

        org = Organization.objects.filter(org_id=org_id).first()
        if(not org):
            raise forms.ValidationError("Unkown Id", code='invalid_orgid')


    def __init__(self, user, *args, **kwargs):
        super(OrganizationListForm, self).__init__(*args, **kwargs)

        org_list = []
        for org in Organization.objects.filter(visible=True).exclude(memberships__user=user):
            org_list.append({
                'name': org.name,
                'id': org.org_id,
                'description': org.description,
                'access':org.access,
                'fee': org.pretty_print_membership_fee()
            })

        self.org_count = len(org_list)
        self.org_list = org_list

class OrganizationPasswordForm(forms.Form):
    org_id = forms.CharField(label='id', max_length=10)
    org_password = forms.CharField(label='password', max_length=10, required=False, widget=forms.PasswordInput)


    def __init__(self, org_id, *args, **kwargs):
        super(OrganizationPasswordForm, self).__init__(*args, **kwargs)

        if(org_id==''):
            return
        
        self.fields['org_id'].initial = org_id
        self.fields['org_id'].disabled = True


    def clean(self, *args , **kwargs):
        super(OrganizationPasswordForm, self).clean(*args ,**kwargs) 

        org_id = self.cleaned_data['org_id']
        org_password = self.cleaned_data['org_password']

        org = Organization.objects.filter(org_id=org_id).first()
        if(not org):
            raise forms.ValidationError("Unkown Id", code='invalid_orgid')

        if(not org.public and org.password!=org_password):
            raise forms.ValidationError("Invalid Password", code='invalid_password')
            

class OrganizationRINForm(forms.Form):
    rin = forms.IntegerField(required=True, label="", widget=forms.TextInput(attrs={'style':'width: 100%'}))

    def clean(self, *args , **kwargs):
        super(OrganizationRINForm, self).clean(*args ,**kwargs) 
        
        rin = self.cleaned_data['rin']

        if rin:
            # Check to see if RIN is 9 digits long
            if(len(str(rin)) != 9):
                raise forms.ValidationError("Invalid Rin", code='invalid_rin')
            
            if(UserProfile.objects.filter(rin=rin)):
                raise forms.ValidationError("Rin already Exists", code='invalid_rin')
            
        return self.cleaned_data

class OrganizationConfirmationForm(forms.Form):
    policy_acceptance = forms.BooleanField(required = True)

    org = None
    pretty_cost = ''
    cost = 0

    def __init__(self, org, *args, **kwargs):
        super(OrganizationConfirmationForm, self).__init__(*args, **kwargs)

        self.org = org
        if(org):
            self.cost = org.membership_fee
            self.pretty_cost = org.pretty_print_membership_fee()



#
# Form Checks
#
def public_organization(wizard):
    data = wizard.get_cleaned_data_for_step('0') or {}
    if(data!={} and 'org_id' in data):
        org_id=data['org_id']
        org = Organization.objects.all().filter(org_id=org_id).first()
        if(org is None):
            return True
        return not org.public
    return True

def has_rin(wizard):
    user = wizard.request.user
    return user.userprofile.rin is None

organization_templates = ["formtools/wizard/organization_management/organization_list.html","formtools/wizard/organization_management/organization_join.html","formtools/wizard/organization_management/rin_confirmation.html","formtools/wizard/organization_management/organization_confirmation.html"]

class JoinOrganizationWizard(SessionWizardView):
    # ? Use: Form to create user
    form_list = [OrganizationListForm, OrganizationPasswordForm, OrganizationRINForm, OrganizationConfirmationForm]

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        user = self.request.user
        userprofile = user.userprofile

        org_id = data['org_id']
        org = Organization.objects.filter(org_id=org_id).first()

        if(org is None):
            return render(self.request, "formtools/wizard/organization_management/form_submission.html", {'success':False})
        
        for form in form_list:
            # if RIN Form is in formlist which means the user set their rin
            if(isinstance(form, OrganizationRINForm)):
                rin = data['rin']
                userprofile.rin = rin
                try:
                    userprofile.save()
                except IntegrityError:
                    return render(self.request, "formtools/wizard/organization_management/form_submission.html", {'success':False})
                break

        if(org.public):
            org.add_user(user)
        else:
            password = data['password']
            if(org.password == password):
                org.add_user(user)
            else:
                return render(self.request, "formtools/wizard/organization_management/form_submission.html", {'success':False})

        
        return render(self.request, "formtools/wizard/organization_management/form_submission.html", {'success':True})

    def get_template_names(self):
        #select display template via current step
        return [organization_templates[int(self.steps.current)]]
    
    #set initial variables for the forms. 
    def get_form_kwargs(self, step):
        initial = super(JoinOrganizationWizard, self).get_form_kwargs(step=step)

        #if step 2
        if step == '0':
            initial['user'] = self.request.user
        if step == '1':
            data = self.get_cleaned_data_for_step('0') or {}
            if(data!={} and 'org_id' in data):
                initial['org_id']=data['org_id']
            else:
                initial['org_id']=''
        if step == '3':
            data = self.get_cleaned_data_for_step('0') or {}
            if(data!={} and 'org_id' in data):
                initial['org']=Organization.objects.filter(org_id=data['org_id']).first()
            else:
                initial['org']=None

        return initial

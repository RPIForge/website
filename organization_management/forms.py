#django imports
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db.models.base import ObjectDoesNotExist 

#class import
from organization_management.models import *
from user_management.models import UserProfile

#custom imports
from formtools.wizard.views import SessionWizardView



class OrganizationListForm(forms.Form):
    org_id = forms.CharField(max_length=8,required=False)

    org_count = 0
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
    pass


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

organization_templates = ["formtools/wizard/organization_management/organization_list.html","formtools/wizard/organization_management/organization_join.html","formtools/wizard/organization_management/rin_confirmation.html","formtools/wizard/organization_management/organization_confirmation.html"]

class JoinOrganizationWizard(SessionWizardView):
    # ? Use: Form to create user
    form_list = [OrganizationListForm, OrganizationPasswordForm, OrganizationRINForm, OrganizationConfirmationForm]


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

        return initial

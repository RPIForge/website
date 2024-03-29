#django imports
from django import forms
from django.shortcuts import redirect, render
from django.core.exceptions import ValidationError

#class import
from user_management.models import *
from machine_management.models import *
from business.utils import get_current_semester
from formtools.wizard.views import SessionWizardView

import datetime

#Machine Selection form
class MachineSelectionForm(forms.Form):
    machine = forms.ModelChoiceField(queryset=Machine.objects.filter(in_use=False).order_by("machine_name"))
    
    def __init__(self, *args, **kwargs):
        super(MachineSelectionForm, self).__init__(*args, **kwargs)
        
        ##incase for grouping
        
        choice_list = []
        for type in MachineType.objects.all():
            typed_choice = []
            for machine in type.machine_set.filter(in_use=False).filter(enabled=True):
                typed_choice.append((machine.id, machine.machine_name))
                
            if(not typed_choice):
                continue
            choice_list.append([type.machine_type_name,typed_choice])
        
        
        self.fields['machine']._set_choices(choice_list)

#Machine Slot usage
class MachineSlotUsageForm(forms.Form):
    #list of slot names and costs
    slot_name_list = []
    slot_cost_dict = {}
    slot_unit_dict = {}
    
    #machine select
    machine = None
    
    
    def __init__(self, machine, *args, **kwargs):
        super(MachineSlotUsageForm, self).__init__(*args, **kwargs)
        
        self.machine = machine
        
        #for each slot in the machine
        for slot in machine.machine_type.machineslot_set.all():
            #get slot name and append to list
            slot_name = slot.slot_name
            self.slot_name_list.append(slot_name)
            
            
            #generate list of slot resources
            choice_list = []
            unit_text = ''
            resource_name = ''
            for resource in slot.allowed_resources.all():
                choice_list.append((resource.id, resource.resource_name))
                self.slot_cost_dict[resource.resource_name] = float(resource.cost_per)
                self.slot_unit_dict[resource.resource_name] = resource.unit
                if(unit_text==''):
                    unit_text=resource.unit
                    resource_name = resource.resource_name
            
            if(choice_list):
                choice_list.sort(key = lambda x: x[1])
            
            #add choice field and decimal field
            self.fields['resource_{}'.format(slot.id)] = forms.ChoiceField(choices=choice_list)
            
            self.fields['ammount_{}'.format(slot.id)] = forms.FloatField(required = True,  min_value=0.01,widget=forms.NumberInput(attrs={'placeholder': unit_text+' of '+resource_name}))

#Usage Length usage
class MachineUsageLength(forms.Form):
    usage_hours = forms.IntegerField(required=False, min_value=0, widget=forms.NumberInput(attrs={'placeholder': 'Hours'}))
    usage_minutes = forms.IntegerField(required=False, min_value=0, max_value=60, widget=forms.NumberInput(attrs={'placeholder': 'Minutes'}))

    def clean(self):
        cleaned_data = super().clean()
        usage_hours = self.cleaned_data['usage_hours']
        usage_minutes = self.cleaned_data['usage_minutes']
        
        if not usage_minutes and not usage_hours:
            raise ValidationError("Time cannot be empty")
        if not usage_minutes and usage_hours > 0:
            usage_minutes = 0
        if not usage_hours and usage_minutes > 0:
            usage_hours = 0
        if usage_minutes <= 0 and usage_hours <= 0:
            raise ValidationError("Time cannot be empty")
            
        self.cleaned_data['usage_hours'] = usage_hours
        self.cleaned_data['usage_minutes'] = usage_minutes
        return cleaned_data

class MachinePolicy(forms.Form):
    policy_acceptance = forms.BooleanField(required = True)
    
    text = "default"
    
    def __init__(self, *args, **kwargs):
        self.text = get_current_semester().buisness_message
        super(MachinePolicy, self).__init__(*args, **kwargs)

class MachineOptions(forms.Form):
    class_usage = forms.BooleanField(required = False)
    own_material = forms.BooleanField(required = False)
    reprint = forms.BooleanField(required = False)

    def __init__(self, machine, *args, **kwargs):  
        super(MachineOptions, self).__init__(*args, **kwargs)

        if(not machine.personal_material_allowed):
            self.fields.pop("own_material")

        


machine_usage_templates = ["formtools/wizard/machine_usage/machine_selection.html","formtools/wizard/machine_usage/resource_selection.html","formtools/wizard/machine_usage/usage_duration.html","formtools/wizard/machine_usage/machine_policy.html", "formtools/wizard/machine_usage/machine_options.html" ]


def machine_has_slots(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step('0') or {}
    if(cleaned_data!={}):
        machine = cleaned_data['machine']
        if(machine.machine_type.machineslot_set.all()):
            return True
        else:
            return False
    return True
    
class MachineUsageWizard(SessionWizardView):
    #list form
    form_list = [MachineSelectionForm, MachineSlotUsageForm, MachineUsageLength, MachinePolicy, MachineOptions]
        
        
        
    def done(self, form_list, **kwargs):
        #get data
        data = self.get_all_cleaned_data()
        machine = data['machine']
        
        #create new usage and set information
        new_usage = Usage()
        new_usage.machine = machine
        new_usage.semester = Semester.objects.get(current=True)
        new_usage.userprofile = self.request.user.userprofile
        new_usage.for_class = data['class_usage']
        new_usage.is_reprint = data['reprint']
        new_usage.own_material = False
        if("own_material" in data):
            new_usage.own_material = data['own_material']
            
        new_usage.save()#to set create_time

        new_usage.set_end_time(data['usage_hours'],data['usage_minutes'])
        new_usage.save()
        
        machine.in_use = True
        machine.current_job = new_usage
        machine.save()
        
        for slot in machine.machine_type.machineslot_set.all():
            #get slot name and append to list
            
            resource_name = 'resource_{}'.format(slot.id)
            amount_name = 'ammount_{}'.format(slot.id)
            
            resource_id = data[resource_name]
            amount = data[amount_name]
            
            new_slot_usage = SlotUsage()
            new_slot_usage.machine_slot = slot
            new_slot_usage.resource = Resource.objects.get(id=resource_id)
            new_slot_usage.amount = amount
            new_slot_usage.usage = new_usage
            new_slot_usage.save()
        
        return render(self.request, "formtools/wizard/machine_usage/form_submission.html", {'success':True})
        
    
    def get_template_names(self):
        #select display template via current step
        return [machine_usage_templates[int(self.steps.current)]]
    
    
    #set initial variables for the forms. 
    def get_form_kwargs(self, step):
        initial = super(MachineUsageWizard, self).get_form_kwargs(step=step)
        #if step 1
        if step == '1' or step == '4':
            try:
                #select machine id from current step
                machine_id = self.request.POST.get('0-machine')
                machine = Machine.objects.get(id=machine_id)
                initial['machine'] = machine
            except:
                try:
                    #for machines after
                    initial = self.get_cleaned_data_for_step("0")
                except:
                    pass

        return initial    
    
    #set template context for forms.
    def get_context_data(self, form, **kwargs):
        #update template for item 1
        context = super(MachineUsageWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == '1':
            context.update({'slot_name_list': form.slot_name_list})
            context.update({'slot_cost_dict': form.slot_cost_dict})
            context.update({'slot_unit_dict': form.slot_unit_dict})
            
        return context
    
    
        
   

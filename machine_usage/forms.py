#django imports
from django import forms

#class import
from user_management.models import *
from machine_management.models import *
from formtools.wizard.views import SessionWizardView


#Machine Selection form
class MachineSelectionForm(forms.Form):
    machine = forms.ModelChoiceField(queryset=Machine.objects.filter(in_use=False)) 

#Machine Slot usage
class MachineSlotUsageForm(forms.Form):
    #list of slot names and costs
    slot_name_list = []
    slot_cost_dict = {}
    
    
    def __init__(self, machine, *args, **kwargs):
        super(MachineSlotUsageForm, self).__init__(*args, **kwargs)
        
        #for each slot in the machine
        for slot in machine.machine_type.machineslot_set.all():
            #get slot name and append to list
            slot_name = slot.slot_name
            self.slot_name_list.append(slot_name)
            
            
            #generate list of slot resources
            choice_list = []
            for resource in slot.allowed_resources.all():
                choice_list.append((resource.id, resource.resource_name))
                self.slot_cost_dict[resource.resource_name] = resource.cost_per
            
            #add choice field and decimal field
            self.fields['{}resource'.format(slot.id)] = forms.ChoiceField(choices=choice_list)
            
            self.fields['{}ammount'.format(slot.id)] = forms.DecimalField()
    
    
machine_usage_forms = [
        ("machine_selection", MachineSelectionForm),
        ("resource_selection", MachineSlotUsageForm)]

machine_usage_templates = ["formtools/wizard/machine_usage/machine_selection.html","formtools/wizard/machine_usage/resource_selection.html"]


class MachineUsageWizard(SessionWizardView):
    #list form
    form_list = [MachineSelectionForm, MachineSlotUsageForm]
        
    def done(self, form_list, **kwargs):
        ### REWRITE THIS ###
        return redirect('/')
    
    def get_template_names(self):
        #display template
        return [machine_usage_templates[int(self.steps.current)]]
    
    
    #set initial variables for the forms. 
    def get_form_kwargs(self, step):
        initial = {}
        
        print(self.request.POST)
        print(step)
        
        if step == '1':
            machine_id = self.request.POST.get('0-machine')
            machine = Machine.objects.get(id=machine_id)
            initial['machine'] = machine

        return initial    
    
    #set template context for forms.
    def get_context_data(self, form, **kwargs):
        context = super(MachineUsageWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == '1':
            context.update({'slot_name_list': form.slot_name_list})
            context.update({'slot_cost_dict': form.slot_cost_dict})
            
        return context
    
    
        
   
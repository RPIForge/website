#django imports
from django import forms

#class import
from user_management.models import *
from machine_management.models import *
from formtools.wizard.views import SessionWizardView


class MachineSelectionForm(forms.Form):
    machine = forms.ModelChoiceField(queryset=Machine.objects.filter(in_use=False)) 

class MachineSlotUsageForm(forms.Form):
    def __init__(self, machine, *args, **kwargs):
        super(MachineSlotUsageForm, self).__init__(*args, **kwargs)
        
        
        slot_list = []
        for slot in machine.machine_type.get_slot_names():
            choice_list = []
            for resource in slot.allowed_resources:
                choice_list.append((resource.id, resource.resoruce_name))
            
            slot_form = forms.ComboField(fields=[forms.ChoiceField(choice_list), forms.DecimalField()])
            slot_form.label = slot.slot_name
            
            slot_list.append(slot_form)
        self.fields['slots'] = forms.ComboField(slot_list)
    


class MachineUsageWizard(SessionWizardView):
    def done(self, form_list, **kwargs):
        print(1)
        return redirect('/page-to-redirect-to-when-done/')
    
    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        
        #if step is None:
        #    step = self.steps.current
        #
        #
        ##try:
        ##    print(data.get('0-machine'))
        ##except:
        ##    print('no data')
        # 
        #print(step,step==1,step=='1')
        #if(step=='1'):
        #    machine_id = data.get('0-machine')
        #    machine = Machine.objects.get(id=machine_id)
        #    form = MachineSlotUsageForm(machine)
        #    return form
        
        
        return form
        
    def get_form_kwargs(self, step):
        kwargs = super(MachineUsageWizard, self).get_form_kwargs(step)
        if step == u'1':
            kwargs['user_id'] = self.request.user.id
        return kwargs


# Importing Django Utils
from django.utils import timezone

#importing functions
from forge import utils

# Importing Models
from machine_management.models import *
from user_management.models import *
from apis.models import *

def clear_usage(machine):
    usage = machine.current_job
    if not usage:
        return False
        
    usage.clear_time = timezone.now()
    usage.complete = True
    if (not usage.error) and (not usage.failed):
        usage.status_message = "Cleared."
    usage.save()

    machine.current_job = None
    machine.current_print_information = None
    
    machine.in_use = False
    machine.save()
    
    return True
def fail_usage(machine):
    if not machine.in_use:
            return False

    usage = machine.current_job
    usage.clear_time = timezone.now()
    usage.failed = True
    usage.status_message = "Failed."
    usage.save()

    utils.send_failure_email(usage)
    return True
    
    
def clear_print(machine):
    print_information = machine.current_print_information
    if(not print_information):
        return False
        
    print_information.end_time = timezone.now()
    print_information.complete = True
    print_information.status_message = "Completed"
    print_information.save()
    
    machine.current_print_information = None
    machine.in_use = False
    machine.save()
    
    return True
    
    
def create_print(machine):
    print_information = machine.current_print_information
    usage = machine.current_job

    if(print_information):
        if(print_information.start_time < timezone.now() - timedelta(minutes = 30)): ##change to end time somehow
            clear_print(machine)
            print_information = None
        else:
            return print_information
    
    
    #if usage was more than a half an hour ago assume it wsa different
    if(usage):
        if(usage.complete):
            clear_usage(machine)
            
        if(usage.start_time < timezone.now() - timedelta(minutes = 30)):
            usage=None
            
    
    #if just usage then set print information to usage    
    if(usage):
        #create new job and set usage
        new_job = JobInformation()
        new_job.status = "Printing"
        new_job.machine = machine
        new_job.usage = usage
        new_job.status_message = "Printing."
        new_job.save()
        
        #set usage print_job
        usage.current_print_information = new_job
        usage.save()
        
        
    else:
        #create new job
        new_job = JobInformation()
        new_job.status = "Printing"
        new_job.machine = machine
        new_job.status_message = "Printing."
        new_job.save()
        
    #set machine print_job
    machine.current_print_information = new_job
    machine.save()

    return new_job


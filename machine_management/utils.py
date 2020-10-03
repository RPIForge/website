

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
     


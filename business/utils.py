# file to keep track of helper functions
# Importing Django Utils


# Importing Models
from business.models import Semester
from machine_management.models import Usage

# Importing Other Libraries
def get_current_semester():
    return Semester.objects.all().filter(current=True).first()


def get_user_usage_semester_cost(user, semester):
    # get all usages of user without org
    usage_list = Usage.objects.all().filter(userprofile=user.userprofile, organization=None)

    # if semester is not none then filter
    if(semester is not None):
        usage_list = usage_list.filter(semester=semester)
    
    #prefetch cost related metrics
    usage_list = usage_list.prefetch_related('machine').prefetch_related('machine__machine_type')\
        .prefetch_related('slotusage_set').prefetch_related('slotusage_set__resource')

    # add totals
    total_cost = 0
    for usage in usage_list:
        total_cost += usage.cost()

    return total_cost
    
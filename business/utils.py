# file to keep track of helper functions
# Importing Django Utils


# Importing Models
from business.models import Semester
from machine_management.models import Usage

# Importing Other Libraries
def get_current_semester():
    return Semester.objects.all().filter(current=True).first()


def get_user_semester_cost(user, semester):
    if(semester is not None):
        usage_list = Usage.objects.all().filter(semester=semester)
    else:
        
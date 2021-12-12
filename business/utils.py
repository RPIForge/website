# file to keep track of helper functions
# Importing Django Utils


# Importing Models
from business.models import Semester


# Importing Other Libraries


def get_current_semester():
    return Semester.objects.all().filter(current=True).first()
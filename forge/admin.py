from django.contrib import admin

from machine_management.models import *
from user_management.models import *
from user_management.admin import *

from django.contrib.auth.models import User, Group

admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(Resource)
admin.site.register(MachineType)
admin.site.register(MachineSlot)
admin.site.register(Machine)
admin.site.register(Semester)
admin.site.register(Usage)
admin.site.register(SlotUsage)

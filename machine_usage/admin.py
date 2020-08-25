from django.contrib import admin

from .models import *

admin.site.register(Resource)
admin.site.register(MachineType)
admin.site.register(MachineSlot)
admin.site.register(Machine)
admin.site.register(Semester)
admin.site.register(Usage)
admin.site.register(SlotUsage)
admin.site.register(UserProfile)

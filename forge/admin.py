from django.contrib import admin

from machine_management.models import *
from business.models import *
from data_management.models import *
from user_management.models import *
from organization_management.models import *
from apis.models import *


from data_management.admin import *
from user_management.admin import *
from organization_management.admin import *

from django.contrib.auth.models import User, Group

#register models to Admin
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Resource)
admin.site.register(MachineType)
admin.site.register(MachineSlot)
admin.site.register(Machine)
admin.site.register(Semester)
admin.site.register(Usage)
admin.site.register(SlotUsage)
admin.site.register(Organization, OrganizationAdmin)


admin.site.register(JobInformation, JobInformationAdmin)

admin.site.register(Key)



from django.urls import path

from . import views
from .forms import *

urlpatterns = [
    #org functions
    path('dyn/org_list_joinable', JoinOrganizationWizard.as_view(condition_dict={'1':public_organization,'2':has_rin}), name='user_list_joinable'),
<<<<<<< HEAD
    path('dyn/org_members', views.list_joinable_organizations, name='active_usage_list_joinable'),
    path('dyn/org_projects', views.list_oragnization_projects, name='usage_list_joinable'),
    path('dyn/org_machines', views.list_joinable_organizations, name='usage_list_joinable'),
=======
    path('dyn/org_members', views.list_organization_membership, name='active_usage_list_joinable'),
   # path('dyn/org_projects', views.list_joinable_organizations, name='org_projects'),
   # path('dyn/org_machines', views.list_joinable_organizations, name='org_machines'),
>>>>>>> 02aa822b06d26bddf4e12ffc49884fdc9251fafd
]
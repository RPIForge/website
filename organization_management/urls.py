from django.urls import path

from . import views

urlpatterns = [
    #org functions
    path('dyn/org_list_joinable', views.list_joinable_organizations, name='user_list_joinable'),
    path('dyn/org_members', views.list_joinable_organizations, name='active_usage_list_joinable'),
    path('dyn/org_projects', views.list_joinable_organizations, name='usage_list_joinable'),
    path('dyn/org_machines', views.list_joinable_organizations, name='usage_list_joinable'),
]
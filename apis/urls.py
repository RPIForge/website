from django.urls import path

from . import views

urlpatterns = [
    #machine endpoints
    path('api/machine', views.machine_endpoint, name='machine_endpoint'),
    path('api/machines/clear', views.clear_machine, name='clear_machine'),
    path('api/machines/fail', views.fail_machine, name='fail_machine'),
    
    #user endpoints
    path('api/users/verify', views.verify_user, name='verify_user'),
    path('api/volunteers/current', views.current_volunteers, name='current_volunteers'),
    
    #billing endpoints
    path('api/billing/charge_sheet', views.charge_sheet, name='charge_sheet'),  

    #organization endpoint
    path('api/organization/join_organization', views.join_organization, name='join_organization'),  

]
    
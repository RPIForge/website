from django.urls import path

from . import views

urlpatterns = [
    #machine endpoints
    path('api/machines', views.machine_endpoint, name='machine_endpoint'),
    path('api/machines/clear', views.clear_machine, name='clear_machine'),
    path('api/machines/fail', views.fail_machine, name='fail_machine'),
    
 
    #octoprint management
    path('api/machines/data', views.machine_data, name='machine_status'), 
    path('api/machines/status', views.machine_status, name='machine_status'),
    path('api/machines/print/temperature', views.machine_temperature, name='machine_temperature'),
    path('api/machines/print/location', views.machine_location, name='machine_location'),
    path('api/machines/print/information', views.machine_information, name='machine_print'),
    
    #user endpoints
    path('api/users/verify', views.verify_user, name='verify_user'),
    path('api/volunteers/current', views.current_volunteers, name='current_volunteers'),
    
    #billing endpoints
    path('api/billing/charge_sheet', views.charge_sheet, name='current_volunteers'),  
]
    
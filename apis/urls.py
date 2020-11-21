from django.urls import path

from . import views

urlpatterns = [
    #machine management
    path('api/machines', views.machine_endpoint, name='machine_endpoint'),
    path('api/machines/clear', views.clear_machine, name='clear_machine'),
    path('api/machines/fail', views.fail_machine, name='fail_machine'),
    
    #octoprint management
    path('api/machines/status', views.machine_status, name='machine_status'),
    path('api/machines/print/temperature', views.machine_temperature, name='machine_temperature'),
    path('api/machines/print/information', views.machine_information, name='machine_print'),
    
    #user management
    path('api/users/verify', views.verify_user, name='verify_user'),

    #Billing management
    path('api/billing/charge_sheet', views.charge_sheet, name='current_volunteers'),
    
]
    
from django.urls import path

from . import views

urlpatterns = [
    #octoprint management
    path('data/machines/data', views.machine_data, name='machine_status'), 
    path('data/machines/status', views.machine_status, name='machine_status'),
    path('data/machines/print/temperature', views.machine_temperature, name='machine_temperature'),
    path('data/machines/print/location', views.machine_location, name='machine_location'),
]
    
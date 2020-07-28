from django.urls import path

from . import views

urlpatterns = [

    path('forms/machine_usage', views.machine_usage, name='machine_usage'),
    path('forms/machine_form', views.generate_machine_form, name='machine_form'),
    path('forms/clear_machine', views.generate_clear_machine_form, name='clear_machine_form'),
    path('forms/failed_usage', views.generate_failed_usage_form, name='failed_usage')
]

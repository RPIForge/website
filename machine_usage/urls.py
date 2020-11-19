from django.urls import path

from . import views
from .forms import *
urlpatterns = [

    path('forms/machine_usage', MachineUsageWizard.as_view(condition_dict={"1":machine_has_slots}), name='machine_usage'),
    path('forms/machine_form', views.generate_machine_form, name='machine_form'),
    path('forms/clear_machine', views.generate_clear_machine_form, name='clear_machine_form'),
    path('forms/failed_usage', views.generate_failed_usage_form, name='failed_usage')
]

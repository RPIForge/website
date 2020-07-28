from django.urls import path

from . import views

urlpatterns = [
    

    path('unverified_email', views.render_unverified_email, name='unverified_email'),
    path('begin_semester', views.render_begin_semester, name='begin_semester'),

    path('forms/force_email_verification', views.render_force_email_verification, name='force_email_verification'),
    
    
    
    path('forms/machine_usage', views.machine_usage, name='machine_usage'),
    path('forms/machine_form', views.generate_machine_form, name='machine_form'),
    path('forms/clear_machine', views.generate_clear_machine_form, name='clear_machine_form'),
    path('forms/failed_usage', views.generate_failed_usage_form, name='failed_usage')
]

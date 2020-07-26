from django.urls import path

from . import views

urlpatterns = [
    path('', views.render_index, name='index'),
    path('our_space', views.render_index, name='our_space'),
    path('equipment', views.render_equipment, name='equipment'),
    path('status', views.render_status, name='status'),
    path('news', views.render_news, name='news'),
    path('hours', views.render_hours, name='hours'),
    path('login', views.render_login, name='login'),
    path('logout', views.log_out, name='logout'),
    path('myforge', views.render_myforge, name='myforge'),

    path('unverified_email', views.render_unverified_email, name='unverified_email'),
    path('begin_semester', views.render_begin_semester, name='begin_semester'),

    path('forms/create_user', views.create_user, name='create_user'),
    path('forms/machine_usage', views.machine_usage, name='machine_usage'),
    path('forms/machine_form', views.generate_machine_form, name='machine_form'),
    path('forms/clear_machine', views.generate_clear_machine_form, name='clear_machine_form'),
    path('forms/failed_usage', views.generate_failed_usage_form, name='failed_usage'),
    path('forms/force_email_verification', views.render_force_email_verification, name='force_email_verification'),

    path('dyn/project_list', views.list_projects, name='project_list'),
    path('dyn/machine_list', views.list_machines, name='machine_list'),
    path('dyn/machine_type_list', views.list_machine_types, name='machine_type_list'),
    path('dyn/resource_list', views.list_resources, name='resource_list'),
    path('dyn/user_list', views.list_users, name='user_list'),
    path('dyn/active_usage_list', views.list_active_usages, name='active_usage_list'),
    path('dyn/usage_list', views.list_usages, name='usage_list'),
    path('dyn/volunteer_dashboard', views.volunteer_dashboard, name='volunteer_dashboard'),

    path('verify_email', views.render_verify_email, name='verify_email'),
    path('resend_verification', views.resend_email_verification, name='resend_verification'),

    path('api/machines', views.machine_endpoint, name='machine_endpoint'),
    path('api/machines/clear', views.clear_machine, name='clear_machine'),
    path('api/machines/fail', views.fail_machine, name='fail_machine'),
]

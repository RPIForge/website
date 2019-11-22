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

    path('dyn/project_list', views.list_projects, name='project_list'),
    path('dyn/machine_list', views.list_machines, name='machine_list'),
    path('dyn/machine_type_list', views.list_machine_types, name='machine_type_list'),
    path('dyn/resource_list', views.list_resources, name='resource_list'),
    path('dyn/user_list', views.list_users, name='user_list'),
    path('dyn/create_user',views.create_user, name='create_user'),
    path('dyn/volunteer_dashboard', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('verify_email',views.render_verify_email, name='verify_email')
]

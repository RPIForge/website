from django.urls import path

from . import views

urlpatterns = [
    #initial myforge path
    path('myforge', views.render_myforge, name='myforge'),
    path('myforge/<path:resource>', views.render_myforge, name='myforge'),
    
    #myforge table lists
    path('dyn/project_list', views.list_projects, name='project_list'),
    path('dyn/machine_list', views.list_machines, name='machine_list'),
    path('dyn/machine_type_list', views.list_machine_types, name='machine_type_list'),
    path('dyn/resource_list', views.list_resources, name='resource_list'),
    path('dyn/user_list', views.list_users, name='user_list'),
    path('dyn/active_usage_list', views.list_active_usages, name='active_usage_list'),
    path('dyn/usage_list', views.list_usages, name='usage_list'),
    
    #chat functionality
    path('dyn/volunteer_chat_join', views.volunteer_chat_join, name='volunteer_chat'),
    path('dyn/chat_history', views.user_chat_history, name='chat_history'),
    path('dyn/manager_chat_history', views.manager_chat_history, name='chat_history'),
    path('dyn/manager_chat_requests', views.manager_chat_requests, name='chat_history'),
    path('chat', views.user_chat, name='chat'), # TODO Move to main urls
    
    #Volunteer dashboard
    path('dyn/volunteer_dashboard', views.volunteer_dashboard, name='volunteer_dashboard')
]
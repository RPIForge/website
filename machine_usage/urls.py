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
]

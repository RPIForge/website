from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('our_space', views.index, name='our_space'),
    path('equipment', views.index, name='equipment'),
    path('status', views.index, name='status'),
    path('news', views.index, name='news'),
    path('hours', views.index, name='hours'),
    path('login', views.index, name='login'),
]

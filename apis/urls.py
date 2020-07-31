from django.urls import path

from . import views

urlpatterns = [
    path('api/machines', views.machine_endpoint, name='machine_endpoint'),
    path('api/machines/clear', views.clear_machine, name='clear_machine'),
    path('api/machines/fail', views.fail_machine, name='fail_machine'),
    path('api/users/verify', views.verify_user, name='verify_user')
]
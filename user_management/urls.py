from django.urls import path

from . import views

urlpatterns = [
    path('forms/create_user', views.create_user, name='create_user'),
    path('verify_email', views.render_verify_email, name='verify_email'),
    path('resend_verification', views.resend_email_verification, name='resend_verification'),
    path('login', views.render_login, name='login'),
    path('logout', views.log_out, name='logout')
]
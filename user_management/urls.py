from django.urls import path

from . import views

urlpatterns = [
    #User functions
    path('begin_semester', views.render_begin_semester, name='begin_semester'),
    path('forms/create_user', views.create_user, name='create_user'),
    path('forms/create_profile', views.create_user, name='create_user'),
    
    #email urls
    path('verify_email', views.render_verify_email, name='verify_email'),
    path('unverified_email', views.render_unverified_email, name='unverified_email'),
    path('resend_verification', views.resend_email_verification, name='resend_verification'),
    path('forms/force_email_verification', views.render_force_email_verification, name='force_email_verification'),
     
    #User State functions
    path('login', views.render_login, name='login'),
    path('logout', views.log_out, name='logout')
]
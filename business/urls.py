from django.urls import path

from . import views

urlpatterns = [
    #Buisness Paths
    path('dyn/billing/list_semester', views.list_semesters, name='list_semester'),
    path('dyn/billing/change_semesters', views.render_change_semesters, name='change_semesters'),
    path('dyn/billing/charge_sheets', views.render_charge_sheet, name='charge_sheet'),
    path('api/billing/user_charge_sheet', views.user_charge_sheet, name='charge_sheet'),
    path('api/billing/org_charge_sheet', views.org_charge_sheet, name='charge_sheet'),

]

from django.urls import path

from . import views

urlpatterns = [

    path('dyn/billing/change_semesters', views.render_change_semesters, name='change_semesters'),
    path('dyn/billing/charge_sheets', views.render_charge_sheet, name='charge_sheet'),

]

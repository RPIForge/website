from django.contrib import admin
from user_management.models import *
from machine_management.models import *
from django.contrib.auth.models import User, Group


class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'user__first_name', 'user__last_name', )


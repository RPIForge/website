from django.contrib import admin

from organization_management.models import *

from django.forms import ModelForm, PasswordInput
from django.contrib.auth.forms import UserChangeForm

from django.utils.safestring import SafeText


class OrganizationAdmin(admin.ModelAdmin):
    # ? Use: Add search fields to user profile admin
    form = UserChangeForm

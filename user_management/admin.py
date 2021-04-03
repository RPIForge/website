from django.contrib import admin
from django.urls import reverse

from user_management.models import *
from user_management.forms import *
from machine_management.models import *
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin

from django import forms
from django.utils.safestring import SafeText

class UserProfileAdmin(admin.ModelAdmin):
    # ? Use: Add search fields to user profile admin
    search_fields = ('user__username', 'user__first_name', 'user__last_name', )


class ForgeUserAdmin(UserAdmin):   
    # ? Use: Add rin, userprofile link, and list of usages to User admin

    #Add fields
    fieldsets = UserAdmin.fieldsets + (
        ('User Properties', {
            'fields': ('get_rin','get_userprofille','get_usages')
        }),
    )
    
    readonly_fields=('get_rin','get_userprofille','get_usages')
    
    #get rin
    def get_rin(self, object):
        return object.userprofile.rin
        
    #get link to user profile
    def get_userprofille(self, object):
        link=reverse("admin:user_management_userprofile_change", args=[object.userprofile.id])
        return SafeText('<li><a href="{}">{}</a></li>'.format(link,object.userprofile))
        
    #get list of usages
    #TODO: Order usages by time
    def get_usages(self, object):
        userprofile = object.userprofile
        usage_list = userprofile.usage_set.all()
        output_string = "<ul style='overflow:hidden; overflow-y:scroll;'>"
        for usage in usage_list:
            link=reverse("admin:machine_management_usage_change", args=[usage.id])
            usage_string = '<li><a href="{}">{}</a></li>'.format(link,usage)
            output_string = output_string + usage_string
        
        output_string = output_string+"</ul>"
        
        usage_text = SafeText(output_string)
        return usage_text
    
    #allow tags and add descriptions
    get_usages.allow_tags = True 
    get_rin.short_description = "Rin"
    get_userprofille.short_description = "User Profile"
    get_usages.short_description = "List of Usages"
        
    
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, ForgeUserAdmin)

class ForgePrintAdmin(admin.ModelAdmin):
    
    #fields =('get_temperature',)
    
    
    readonly_fields=('get_temperature',)
    
    
    def get_temperature(self, object):
        return "<iframe src='/api/machines/print/temperature?job_id={}&display_graph=1' /></iframe>".format(object.id)
        
    get_temperature.allow_tags = True 
    get_temperature.short_description = "Temperature Information"

        

from django.contrib import admin

class OrganizationAdmin(admin.ModelAdmin):
    # ? Use: Add search fields to user profile admin
    readonly_fields=('org_id',)
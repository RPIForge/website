#django imports
from django import template

#model improts
from organization_management.models import *

#register template libarry
register = template.Library()

@register.filter(name='in_org')
def in_org(user):
    return OrganizationMembership.objects.filter(user=user).first() is not None

@register.filter(name='is_org_manager')
def is_org_manager(user):
    """Removes all values of arg from the given string"""
    return OrganizationMembership.objects.fitler(user=user,manager=True).first() is not None
from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='in_group')
def in_group(user, group_name):
	try:
		group = Group.objects.get(name=group_name)
	except Group.DoesNotExist:
		return False

	#for g in user.groups.all():
	#	print(group_name + " " + str(g))

	return group in user.groups.all()
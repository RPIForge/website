from django.conf import settings # import the settings file

# ! type: Helper function
# ! function: generate channels url for templates
# ? required: 
# ? returns: Dictionary with channels url
# TODO: 
def channels_url(request):
    url = settings.CHAT_SITE+'/user/info'
    
    if request.user.is_authenticated:
        url=url+"?uuid={}".format(request.user.userprofile.uuid)
        url=url+"&name={}".format(request.user.get_full_name())
        url=url+"&email={}".format(request.user.email)
    
    
    
    return {'CHANNELS_URL': url}

def source_url(request):
    return {'ROOT_URL':request.get_host()}

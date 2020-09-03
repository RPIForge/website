from django.conf import settings # import the settings file

def channels_url(request):
    url="http://"+settings.CHAT_SITE_URL+":"+str(settings.CHAT_SITE_PORT)+"/user/info"
    if request.user.is_authenticated:
        url=url+"?uuid={}".format(request.user.userprofile.uuid)
        url=url+"&name={}".format(request.user.get_full_name())
        url=url+"&email={}".format(request.user.email)
    
    
    return {'CHANNELS_URL': url}
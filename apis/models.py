from django.db import models

import secrets


def generate_key():
    token = secrets.token_urlsafe(15)
    return token[:15]
    
class Key(models.Model):
    user_id = models.CharField(max_length=255, unique=True)
    key = models.CharField(max_length=15, default=generate_key)  
    
    def __str__(self):
        return "{}".format(self.user_id)
        


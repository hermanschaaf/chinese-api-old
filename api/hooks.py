import uuid

from mongoengine.django.auth import User
from mongoengine.signals import post_save

import auth.documents

def create_api_key(sender, document, created):
    if created == True:
        key = unicode(uuid.uuid4())
        api_key = auth.documents.ApiKey(user=document, key=key, domains=[])
        api_key.save()

post_save.connect(create_api_key, sender=User)
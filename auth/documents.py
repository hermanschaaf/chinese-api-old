from mongoengine import (Document, IntField, BooleanField, 
    ListField, StringField, DictField, ReferenceField)
from mongoengine import ValidationError
from mongoengine.django.auth import User

from util import is_valid_domain, is_valid_key

class ApiKey(Document):
    """
    These are the users who will have access to the API
    """
    user = ReferenceField('User', required=True, unique=False) # reference field to user document
    key = StringField(required=True, unique=True) # api key, which will also be the app name
    secret = StringField(required=False) # secret key (not used now, maybe later)
    domains = ListField(StringField())  # allowed domains for this Api Key

    meta = {
        'indexes': ['key'],
    }

    def __unicode__(self):
        return self.key

    def save(self, *args, **kwargs):
        self.key = self.key.lower()
        if not is_valid_key(self.key):
            raise ValidationError("Invalid key. Must be alphanumeric with dashes, but not beginning or ending with dash.")
        if not all(map(is_valid_domain, self.domains)):
            raise ValidationError("One or more domains are invalid.") # TODO: make this error more useful
        super(ApiKey, self).save(*args, **kwargs)

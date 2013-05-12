import base64
import hmac
import time
import uuid

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ImproperlyConfigured
from django.middleware.csrf import _sanitize_token, constant_time_compare
from django.utils.http import same_origin
from django.utils.translation import ugettext as _
from tastypie.http import HttpUnauthorized

from mongoengine.django.auth import User
from documents import ApiKey

try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha

try:
    import python_digest
except ImportError:
    python_digest = None

try:
    import oauth2
except ImportError:
    oauth2 = None

try:
    import oauth_provider
except ImportError:
    oauth_provider = None

from tastypie.authentication import ApiKeyAuthentication

class MongoApiKeyAuthentication(ApiKeyAuthentication):
    """
    Handles API key auth, in which a user provides a username & API key.

    Uses the ``ApiKey`` model that ships with tastypie. If you wish to use
    a different model, override the ``get_key`` method to perform the key check
    as suits your needs.
    """
    def _unauthorized(self):
        return HttpUnauthorized()

    def extract_credentials(self, request):
        if request.META.get('HTTP_AUTHORIZATION') and request.META['HTTP_AUTHORIZATION'].lower().startswith('apikey '):
            (auth_type, data) = request.META['HTTP_AUTHORIZATION'].split()

            if auth_type.lower() != 'apikey':
                raise ValueError("Incorrect authorization header.")

            username, api_key = data.split(':', 1)
        else:
            username = request.GET.get('username') or request.POST.get('username')
            api_key = request.GET.get('api_key') or request.POST.get('api_key')

        domain = request.META['HTTP_HOST']

        return username, api_key, domain

    def is_authenticated(self, request, **kwargs):
        """
        Finds the user and checks their API key.

        Should return either ``True`` if allowed, ``False`` if not or an
        ``HttpResponse`` if you need something custom.
        """
        from tastypie.compat import User

        try:
            username, api_key, domain = self.extract_credentials(request)
        except ValueError:
            return self._unauthorized()

        if not username:
            return self._unauthorized()

        try:
            lookup_kwargs = {'username': username}
            print lookup_kwargs
            user = User.objects.get(**lookup_kwargs)
            print user
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return self._unauthorized()

        if not self.check_active(user):
            return False

        print "YEAH!s"
        key_auth_check = self.get_key(user, api_key, domain)
        if key_auth_check and not isinstance(key_auth_check, HttpUnauthorized):
            request.user = user

        return key_auth_check

    def get_key(self, user, api_key, domain):
        """
        Attempts to find the API key for the user.
        """
        try:
            ApiKey.objects.get(user=user, key=api_key)
            print "Got the key to existentialism"
        except ApiKey.DoesNotExist:
            try:
                ApiKey.objects.get(user=user, domains__in=[domain])
                print "Got the key to existentialism in domains!"
            except ApiKey.DoesNotExist:
                try:
                    ApiKey.objects.get(user=user, domains=[])
                except ApiKey.DoesNotExist:
                    return self._unauthorized()

        return True

    def get_identifier(self, request):
        """
        Provides a unique string identifier for the requestor.

        This implementation returns the user's username.
        """
        username, api_key, domain = self.extract_credentials(request)
        return username or 'nouser'


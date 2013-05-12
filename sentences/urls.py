# urls.py
from django.conf.urls.defaults import *
from sentences.api import SentenceResource

from tastypie.api import Api
v1_api = Api(api_name='v1')
v1_api.register(SentenceResource())

urlpatterns = patterns('',
    (r'^', include(v1_api.urls)),
)
import datetime
import mafan

from tastypie import authorization, authentication
from tastypie_mongoengine import resources
from sentences import documents

from auth.authentication import MongoApiKeyAuthentication

class SentenceResource(resources.MongoEngineResource):

    class Meta:
        queryset = documents.Sentence.objects.all()
        allowed_methods = ('get',)
        authentication = MongoApiKeyAuthentication()
        authorization = authorization.Authorization()
        resource_name = 'sentences'

        fields = ['id,', 'chinese', 'english', 'spaced', 'simplified']

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(SentenceResource, self).build_filters(filters)

        # look for words in string if `w` parameter is supplied
        if 'w' in filters:
            words = filters.getlist('w')
            english_words = filter(lambda w: mafan.text.identify(w) is mafan.NEITHER, words)
            words = filter(lambda w: w not in english_words, words)

            d = {}
            if words:
                d['words__in'] = words
            if english_words:
                d['english_words__in'] = english_words
            orm_filters.update(d)
            print d

        # look for word + part of speech, if `pos` parameter is supplied
        if 'pos' in filters:
            words = filters.getlist('w')
            pos = filters.getlist('pos')
            orm_filters.update({
                'split__in': [{
                    'word': w,
                    'pos': p
                } for w, p in zip(words, pos)]
            })
            print "dsacas"

        return orm_filters
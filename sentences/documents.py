from mongoengine import (Document, IntField, BooleanField, 
    ListField, StringField, DictField)
from mongoengine import ValidationError

class Sentence(Document):
    """
    These are the users who will have access to the API
    """
    chinese = StringField(required=True)
    english = StringField(required=False)
    words = ListField(required=True)
    english_words = ListField(required=True)
    split = ListField(DictField())
    simplified = BooleanField(default=True)
    source = StringField(required=False)
    length = IntField(required=True)

    def __unicode__(self):
        return self.chinese

    def save(self, *args, **kwargs):
        self.length = len(self.chinese)
        words = split_text(self.chinese, include_part_of_speech=True, strip_english=True, strip_numbers=True)
        self.split = map(lambda w: {'word':w[0], 'pos': w[1]}, words)
        self.words = map(lambda w: w[0], words)
        self.english_words = re.findall(r'\b\S+\b', self.english)
        self.spaced = ' '.join(split_text(self.chinese))
        super(Sentence, self).save(*args, **kwargs)

    meta = {
        'allow_inheritance': True,
        'indexes': ['chinese', 'english', 'words', 'english_words', 'simplified'],
        'ordering': ['-length']
    }
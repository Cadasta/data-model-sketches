from django.db.models import Model
from django.db import models
from django.contrib.postgres.fields import JSONField

from bitemporal import bitemporal, TemporalForeignKey

from cadasta.core.models import RandomIDModel

from .project import Project


# This is all transcribed more or less verbatim from the SpatialDev
# database schema.  We need to think about how this is going to work
# with GeoODK or whatever we decide to use for data collection.  I
# think the form definitions are mostly OK -- it's just a matter of
# sorting out what IDs and things we use to connect to the data
# collection framework.
#
# Actually, looking at this now a second time, we might want to
# abstract some of this a little, since it's very much tied directly
# to the ODK data schemas, as far as I can tell.  We'll definitely
# want to extend the field types to include more geometry types, for
# example, but there may be more that we could do.
#
# Further down the road, we'll want to add some models to represent
# mapping from questionnaire data to the
# party/spatial-unit/relationship models.

@bitemporal
class Questionnaire(Model):
    raw_form = JSONField()
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    publish = models.BooleanField(default=True)
    project = TemporalForeignKey(Project)
    id_string = models.CharField(max_length=200)
    form_id = models.PositiveIntegerField()


@bitemporal
class QuestionSection(Model):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    publish = models.BooleanField(default=True)
    questionnaire = TemporalForeignKey(Questionnaire)


@bitemporal
class QuestionGroup(Model):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    section = TemporalForeignKey(QuestionSection)
    parent = TemporalForeignKey('self')
    questionnaire = TemporalForeignKey(Questionnaire)


@bitemporal
class Question(Model):
    TYPE_CHOICES = (('TX', 'text'),
                    ('EN', 'end'),
                    ('PH', 'phonenumber'),
                    ('TD', 'today'),
                    ('ST', 'start'),
                    ('DI', 'deviceid'),
                    ('DA', 'date'),
                    ('DT', 'dateTime'),
                    ('PH', 'photo'),
                    ('S1', 'select one'),
                    ('GE', 'geopoint'),
                    ('NO', 'note'),
                    ('IN', 'integer'),
                    ('DE', 'decimal'),
                    ('SI', 'subscriberid'),
                    ('SA', 'select all that apply'),
                    ('CA', 'calculate'),
                    ('RE', 'repeat'),
                    ('GR', 'group'))

    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    section = TemporalForeignKey(QuestionSection)
    group = TemporalForeignKey(QuestionGroup)
    questionnaire = TemporalForeignKey(Questionnaire)

    def has_options(self):
        return self.type in ['S1', 'SA']


@bitemporal
class QuestionOption(Model):
    question = TemporalForeignKey(Question)
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)


@bitemporal
class RawQuestionnaireData(RandomIDModel):
    questionnaire = TemporalForeignKey(Questionnaire)
    data = JSONField(null=True, default=dict())


@bitemporal
class QuestionRespondent(RandomIDModel):
    questionnaire = TemporalForeignKey(Questionnaire)
    uuid = models.UUIDField()
    ona_data_id = models.CharField(max_length=100)


@bitemporal
class QuestionResponse(RandomIDModel):
    respondent = TemporalForeignKey(QuestionRespondent)
    question = TemporalForeignKey(Question)
    answer = models.CharField(max_length=200)

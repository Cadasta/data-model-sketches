import functools
import operator

from django.contrib.contenttypes.models import ContentType
from django.db import models

from bitemporal import bitemporal, TemporalGenericForeignKey

from cadasta.core.models import RandomIDModel, ID_FIELD_LENGTH

from .project import Project
from .attributes import JSONAttributesField


@bitemporal
class Resource(RandomIDModel):
    """
    A resource is an uploaded file of some type associated with an
    entity (party, parcel, some sort of relationship, project or
    organization).
    """

    # Resources are associated with an individual project.
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # Uses S3 storage.
    resource = models.FileField(upload_to='resources')
    mime_type = models.CharField(max_length=100)

    # Resource type: used to manage range of allowed attributes.
    type = models.CharField(max_length=64)

    # JSON attributes field with management of allowed members.
    attributes = JSONAttributesField()

    # Make a generic relation from resources to the objects that they're
    # resources for.

    # Restrict ContentType foreign key to Cadasta core models.
    model_names = ['party', 'party_relationship',
                   'spatial_unit', 'spatial_unit_relationship',
                   'tenure_relationship', 'organization', 'project',
                   'questionnaire', 'question']
    limit = functools.reduce([models.Q(app_label='cadasta', model=m)
                              for m in model_names], operator.or_)
    obj_type = models.ForeignKey(ContentType,
                                 on_delete=models.CASCADE,
                                 limit_choices_to=limit)

    # The type of the obj_id field should match that of the primary
    # key of the target models.
    obj_id = models.CharField(max_length=ID_FIELD_LENGTH)
    obj = TemporalGenericForeignKey('content_type', 'obj_id',
                                    on_delete=bitemporal.CASCADE)

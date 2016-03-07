from django.db.models import Model
from django.db import models

from bitemporal import bitemporal, TemporalForeignKey

from cadasta.core.models import RandomIDModel

from .project import Project
from .party import Party
from .spatial_unit import SpatialUnit
from .attributes import JSONAttributesField


# Should tenure relationships also appear as a many-to-many field in
# Party and/or Parcel, through the TenureRelationship class?  Not sure
# whether that would be a more helpful way to look at it, since there
# really *is* an m:n relationship between parties and parcels in this
# case.

@bitemporal
class TenureRelationshipType(Model):
    """
    Tenure relationship types, e.g. freehold (right), occupancy
    (right), national park law (restriction), etc.
    """
    TYPE_CHOICES = (('RIGHT', 'Right'),
                    ('RESTR', 'Restriction'),
                    ('RESPO', 'Responsibility'))

    # All tenure relationship types are associated with a single
    # project.
    project = TemporalForeignKey(Project, on_delete=bitemporal.CASCADE)

    # Basic type: right, restriction or responsibility.
    type = models.CharField(max_length=5, choices=TYPE_CHOICES,
                            default='RIGHT')

    # Short name for tenure relationship type (e.g. "freehold",
    # "easement", "tenancy").
    name = models.CharField(max_length=100)

    # Long human-readable name for relationship type.
    description = models.TextField()


@bitemporal
class TenureRelationship(RandomIDModel):
    """
    A tenure relationship between a single party and a single spatial
    unit: has a type and a set of attributes.
    """

    # All tenure relationships are associated with a single project.
    project = models.ForeignKey(Project)

    # The party and spatial unit involved in the relationship.
    party = TemporalForeignKey(Party, on_delete=bitemporal.CASCADE)
    spatial_unit = TemporalForeignKey(SpatialUnit,
                                      on_delete=bitemporal.CASCADE)

    # Relationship type: used to manage range of allowed attributes.
    type = TemporalForeignKey(TenureRelationshipType)

    # JSON attributes field with management of allowed members.
    attributes = JSONAttributesField()

from django.db import models
from cadasta.core.models import RandomIDModel
from django.contrib.gis.db.models import GeometryField

from bitemporal import bitemporal, TemporalForeignKey, TemporalManyToManyField

from .project import Project
from .attributes import JSONAttributesField


@bitemporal
class SpatialUnit(RandomIDModel):
    """
    A single spatial unit: has a type, an optional geometry, a
    type-dependent set of attributes and a set of relationships to
    other spatial units.

    """

    # Possible spatial unit types: TYPE_CHOICES is the well-known name
    # used by the JSONAttributesField field type to manage the range
    # of allowed attribute fields.  The following list of spatial unit
    # types is obviously non-exhaustive.  I've included a
    # "miscellaneous" type to cover things like rights of way,
    # national park boundaries and so on, which would be distinguihsed
    # by attributes.
    PARCEL = 'PA'
    COMMUNITY_BOUNDARY = 'CB'
    BUILDING = 'BU'
    APARTMENT = 'AP'
    PROJECT_EXTENT = 'PX'
    RIGHT_OF_WAY = 'RW'
    UTILITY_CORRIDOR = 'UC'
    NATIONAL_PARK_BOUNDARY = 'NP'
    MISCELLANEOUS = 'MI'
    TYPE_CHOICES = ((PARCEL,                 'Parcel'),
                    (COMMUNITY_BOUNDARY,     'Community boundary'),
                    (BUILDING,               'Building'),
                    (APARTMENT,              'Apartment'),
                    (PROJECT_EXTENT,         'Project extent'),
                    (RIGHT_OF_WAY,           'Right-of-way'),
                    (UTILITY_CORRIDOR,       'Utility corridor'),
                    (NATIONAL_PARK_BOUNDARY, 'National park boundary'),
                    (MISCELLANEOUS,          'Miscellaneous'))

    # All spatial units are associated with a single project.
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # Spatial unit geometry is optional: some spatial units may only
    # have a textual description of their location.
    geometry = GeometryField(null=True)

    # Spatial unit type: used to manage range of allowed attributes.
    type = models.CharField(max_length=2,
                            choices=TYPE_CHOICES, default=PARCEL)

    # JSON attributes field with management of allowed members.
    attributes = JSONAttributesField()

    # Spatial unit-spatial unit relationships: includes spatial
    # containment and split/merge relationships.
    relationships = TemporalManyToManyField(
        'self', through='SpatialUnitRelationship',
        through_fields=('su1', 'su2')
    )


@bitemporal
class SpatialUnitRelationship(RandomIDModel):
    """
    A relationship between spatial units: encodes simple logical terms
    like ``su1 is-contained-in su2`` or ``su1 is-split-of su2``.  May
    have additional attributes.
    """

    # Possible spatial unit relationship types: TYPE_CHOICES is the
    # well-known name used by the JSONAttributesField field type to
    # manage the range of allowed attribute fields.
    TYPE_CHOICES = (('C', 'is-contained-in'),
                    ('S', 'is-split-of'),
                    ('M', 'is-merge-of'))

    # All spatial unit relationships are associated with a single
    # project.
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # Spatial units in the relationship.
    su1 = TemporalForeignKey(SpatialUnit, on_delete=bitemporal.CASCADE)
    su2 = TemporalForeignKey(SpatialUnit, on_delete=bitemporal.CASCADE)

    # Spatial unit relationship type: used to manage range of allowed
    # attributes.
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    # JSON attributes field with management of allowed members.
    attributes = JSONAttributesField()

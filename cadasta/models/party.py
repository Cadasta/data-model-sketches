from django.db import models
from cadasta.core.models import RandomIDModel
from bitemporal import bitemporal, TemporalForeignKey, TemporalManyToManyField

from .project import Project
from .attributes import JSONAttributesField


@bitemporal
class Party(RandomIDModel):
    """
    A single party: has a name, a type, a type-dependent set of
    attributes and relationships with other parties and spatial units
    (i.e. tenure relationships).

    """

    # Possible party types: TYPE_CHOICES is the well-known name used
    # by the JSONAttributesField field type to manage the range of
    # allowed attribute fields.
    INDIVIDUAL = 'IN'
    CORPORATION = 'CO'
    GROUP = 'GR'
    TYPE_CHOICES = ((INDIVIDUAL,  'Individual'),
                    (CORPORATION, 'Corporation'),
                    (GROUP,       'Group'))

    # All parties are associated with a single project.
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # All parties have a name: for individuals, this is the full name,
    # while for groups and corporate entities, it's whatever name is
    # conventionally used to identify the organisation.
    name = models.CharField(max_length=200)

    # Party type: used to manage range of allowed attributes.
    type = models.CharField(max_length=2,
                            choices=TYPE_CHOICES, default=INDIVIDUAL)

    # JSON attributes field with management of allowed members.
    attributes = JSONAttributesField()

    # Party-party relationships: includes things like family
    # relationships and group memberships.
    relationships = TemporalManyToManyField(
        'self', through='PartyRelationship',
        through_fields=('party1', 'party2')
    )

    # Tenure relationships.
    tenure_relationships = TemporalManyToManyField(
        'SpatialUnit', through='TenureRelationship'
    )


@bitemporal
class PartyRelationship(RandomIDModel):
    """
    A relationship between parties: encodes simple logical terms like
    ``party1 is-spouse-of party2`` or ``party1 is-member-of party2``.
    May have additional type-dependent attributes.

    """

    # Possible party relationship types: TYPE_CHOICES is the
    # well-known name used by the JSONAttributesField field type to
    # manage the range of allowed attribute fields.
    TYPE_CHOICES = (('S', 'is-spouse-of'),
                    ('C', 'is-child-of'),
                    ('M', 'is-member-of'))

    # All party relationships are associated with a single project.
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # Parties to the relationship.
    party1 = TemporalForeignKey(Party, on_delete=bitemporal.CASCADE)
    party2 = TemporalForeignKey(Party, on_delete=bitemporal.CASCADE)

    # Party relationship type: used to manage range of allowed attributes.
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    # JSON attributes field with management of allowed members.
    attributes = JSONAttributesField()

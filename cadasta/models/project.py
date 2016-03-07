from django.db.models import Model
from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django_countries.fields import CountryField
from bitemporal import TemporalForeignKey

from .organization import Organization


# Projects don't need version tracking, so they're just normal Django
# models.  If a project has a spatial extent assigned, it's stored as
# a ProjectExtent spatial unit.

class Project(Model):
    name = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization)
    country = CountryField()
    description = models.TextField(null=True)
    logo = TemporalForeignKey('Resource')
    urls = ArrayField(models.URLField())
    contacts = JSONField()  # List of JSON-ised hCard records.
    geometry = TemporalForeignKey('SpatialUnit')
    archived = models.BooleanField(default=False)

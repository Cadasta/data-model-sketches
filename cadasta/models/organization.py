from django.db.models import Model
from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from bitemporal import TemporalForeignKey


# Organisations don't need version tracking, so they're just normal
# Django models.

class Organization(Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True)
    logo = TemporalForeignKey('Resource')
    urls = ArrayField(models.URLField())
    contacts = JSONField()  # List of JSON-ised hCard records.
    users = models.ManyToManyField('User')  # Members of the organization.
    archived = models.BooleanField(default=False)

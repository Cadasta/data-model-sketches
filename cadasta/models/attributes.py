from django.db.models import Model
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from bitemporal import bitemporal

from .organization import Organization
from .project import Project


class AttributeManager(models.Manager):
    """
    Custom manager for attributes: just adds a filter to get the
    allowed attribute set for a given object.

    """
    def attribute_set(self, obj):
        """
        Filter queryset for the attributes associated with a particular
        object.
        """
        project = getattr(obj, 'project', None)
        obj_type = ContentType.objects.get_for_model(obj)
        obj_subtype = getattr(obj, 'type', '')
        organization = getattr(project, 'organization', None)
        # NOT QUITE RIGHT: NEEDS TO DEAL WITH DEFAULTING
        # (organization=None, project=None) AND SUBTYPING.  SOMETHING
        # LIKE THIS THOUGH...
        return self.filter(organization=organization, project=project,
                           obj_type=obj_type, obj_subtype=obj_subtype)


@bitemporal
class Attribute(Model):
    """
    Attribute definitions: sets of attributes allowed for different
    object types, keyed on organization, project, Django model class
    and optional model "subtype".  Default attribute sets for
    organizations have project=None; system default attribute sets
    have organization=None and project=None.

    Attributes within attribute sets are ordered by an integer index
    (mainly used for display in the front-end) and have:

     * a name (used for the JSON field name);

     * a long human-readable name;

     * a base type (text, number, etc.);

     * an optional "full" type (used to control detailed validation
       and normalisation -- values might be things like
       "id-post-code", "gb-driving-license-number",
       "us-telephone-number");

     * a presence field saying whether the a value for the attribute
       is required or optional (the third "delete" option can be used
       to remove attributes defined for a particular object type for
       selected subtypes).

    """
    BASE_TYPE_CHOICES = (
        ('NO', 'Number'),
        ('IN', 'Integer'),
        ('FR', 'Number with fraction'),
        ('TX', 'Text'),
    )
    PRESENCE_CHOICES = (
        ('R', 'Required'),
        ('O', 'Optional'),
        ('D', 'Delete'),
    )

    objects = AttributeManager()

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    obj_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    obj_subtype = models.CharField(max_length=100)

    index = models.IntegerField()
    name = models.CharField(max_length=100)
    longname = models.TextField()
    base_type = models.CharField(max_length=2, choices=BASE_TYPE_CHOICES)
    full_type = models.CharField(max_length=100)
    presence = models.CharField(max_length=1, choices=PRESENCE_CHOICES,
                                default='O')

    class Meta:
        index_together = ['organization', 'project', 'obj_type', 'obj_subtype']
        ordering = ['index']


class JSONAttributesField(JSONField):
    """
    This is just like a normal ``JSONField`` field except that it is
    constrained to contain a single JSON object, and uses the
    ``Attribute`` model defined above to validate assignments to elements
    of that object.

    The way this is supposed to work is as follows:

    When you first attempt to assign to a member of a
    ``JSONAttributesField``, the class of which the field is a member
    is used to determine a project (from the class's ``project`` field
    if it has one), content type (from the class) and model subtype
    (from the object's ``type`` field if it has one).  These values are
    used to look up an attribute set, and this is then used to handle
    validation of assignments to the JSON field.

    """

    # NOT SURE HOW TO IMPLEMENT THIS YET...
    def something_something_something(self, obj):
        self.attrs = Attribute.objects.attribute_set(obj)

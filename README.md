Sketches for Cadasta platform data model.

## Bitemporal models

The `bitemporal` package contains a class decorator `bitemporal` and a
number of relation field definitions.  The decorator modifies a Django
model class definition to:

1. Include bitemporal effective and assert time fields;

2. Use a composite primary key made up of the original model's primary
   key plus the initial effective and assert time columns;

3. Perform the appropriate temporal insert, update and delete
   operations when the model's `save` and `delete` methods are called.

You're supposed to use it as:

```
  @bitemporal
  class NewModel(BaseModelClass):
      etc.
```

No other changes to the class definition should be needed.

Foreign keys into bitemporal tables need to be treated specially.  The
`bitemporal` package contains `TemporalForeignKey`,
`TemporalManyToManyField` and `TemporalOneToOneField` Django field
types to use for these situations.


## Organizations and projects

Mostly simple, I think...


## Attributes

This still seems like the most difficult thing to manage.  Here are
what I think are the requirements for this:

1. It should be possible to store any set of attributes for parties,
   spatial units, relationships (party, spatial unit and tenure) and
   resources.

2. The exact set of attributes that can be stored for a particular
   entity depends on the type of the entity: a party representing an
   individual person has a different set of attributes from a party
   representing a corporation; a spatial unit representing a building
   has a different set of attributes from a spatial unit representing
   a community boundary; and so on.

3. The "type" of an entity includes both its Python class (party,
   spatial unit, tenure relationship, etc.) and its "subtype" (person
   vs. corporation vs. group for parties; parcel vs. building
   vs. community boundary vs. whatever for spatial units; the various
   kinds of relationships; etc.).  This subtype is managed using a
   `type` field in the party, spatial unit, etc. classes.

4. It should be possible to manage the sets of attributes allowed for
   given entity types programmatically on a project and organization
   basis.  Eventually this functionality may be exposed in the
   front-end so that a project manager can change the sets of
   attributes allowed for different entity types.

5. It should be possible for the front-end to find out what types of
   entities exist and what attributes are allowed for each of those
   types.  This information should be detailed enough for the
   front-end to do accurate validation on user input for the different
   attributes.

This is all managed by a single `Attribute` class (with a custom
manager), and a `JSONAttributesField` Django field class.  A
`JSONAttributesField` field behaves just like a normal `JSONField`
field, except that it uses the Python class of the object in which
it's embedded, along with the `type` field of the object, to decide on
the allowed set of attributes for the JSON field.

The initial implementation of `JSONAttributesField` can be a "do
nothing" sub-class derived from `JSONField`, allowing us to defer
implementation of the more complicated validated attribute field
class.


## Parties and spatial units

There is one `Party` model and one `SpatialUnit` model, with different
party and spatial unit types distinguished by a `type` choice field.


## Relationships

All relationships are handled as many-to-many fields: party-party
relationships and tenure relationships are defined within the `Party`
model, and spatial unit-spatial unit relationships within the
`SpatialUnit` model.  All of the relationship types have a "through"
class used to carry extra attributes about the relationship in a
`JSONAttributesField` field.

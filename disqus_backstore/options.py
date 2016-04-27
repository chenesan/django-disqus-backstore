from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.datastructures import ImmutableList
from django.utils.functional import cached_property
from django.utils.text import camel_case_to_spaces


IMMUTABLE_WARNING = (
    "The return type of '%s' should never be mutated. If you want to manipulate this list "
    "for your own use, make a copy first."
)

def make_immutable_fields_list(name, data):
    return ImmutableList(data, warning=IMMUTABLE_WARNING % name)    

class DisqusOptions(object):
    abstract = False
    swapped = False
    ordering = None

    fields = dict()

    def __init__(self, *args, **kwargs):
        self.managers = []
        self.fields = []
        self.fields_map = dict()
        
        self.virtual_fields = []
        self.default_related_name = None
        self.apps = apps
        
    def contribute_to_class(self, cls, name):
        self.model = cls
        cls._meta = self
        self.object_name = cls.__name__
        self.model_name = self.object_name.lower()
        self.verbose_name = camel_case_to_spaces(self.object_name)
        self.verbose_name_plural = self.verbose_name + 's'
        self.concrete_model = self.model
        self.setup_pk(self.model.id)


    @cached_property
    def concrete_fields(self):
        """
        Returns a list of all concrete fields on the model and its parents.

        Private API intended only to be used by Django itself; get_fields()
        combined with filtering of field properties is the public API for
        obtaining this field list.
        """
        return make_immutable_fields_list(
            "concrete_fields", (f for f in self.fields if f.concrete)
        )
        
    def add_field(self, field, virtual=False):
        self.fields.append(field)
        self.fields_map[field.name] = field

    def setup_pk(self, field):
        self.pk = field

    def get_field(self, field_name):
        field = self.fields_map.get(field_name)
        if not field:
            raise FieldDoesNotExist('{field} not exist.'.format(field=field_name))
        return field

        
    @cached_property
    def many_to_many(self):
        """
        Returns a list of all many to many fields on the model and its parents.

        Private API intended only to be used by Django itself; get_fields()
        combined with filtering of field properties is the public API for
        obtaining this list.
        """
        return make_immutable_fields_list(
            "many_to_many",
            (f for f in self._get_fields(reverse=False)
            if f.is_relation and f.many_to_many)
        )

    @cached_property
    def related_objects(self):
        """
        Returns all related objects pointing to the current model. The related
        objects can come from a one-to-one, one-to-many, or many-to-many field
        relation type.

        Private API intended only to be used by Django itself; get_fields()
        combined with filtering of field properties is the public API for
        obtaining this field list.
        """
        all_related_fields = self._get_fields(forward=False, reverse=True, include_hidden=True)
        return make_immutable_fields_list(
            "related_objects",
            (obj for obj in all_related_fields
            if not obj.hidden or obj.field.many_to_many)
        )

    @cached_property
    def _forward_fields_map(self):
        res = {}
        fields = self._get_fields(reverse=False)
        for field in fields:
            res[field.name] = field
            # Due to the way Django's internals work, get_field() should also
            # be able to fetch a field by attname. In the case of a concrete
            # field with relation, includes the *_id name too
            try:
                res[field.attname] = field
            except AttributeError:
                pass
        return res
                
    def _get_fields(self, reverse=True, forward=True):
        return tuple(field for field_name, field in self.fields_map.items())
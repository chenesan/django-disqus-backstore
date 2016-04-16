from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.text import camel_case_to_spaces


class DisqusOptions(object):
    abstract = False
    swapped = False
    ordering = None

    fields = dict()

    def __init__(self, *args, **kwargs):
        self.managers = []
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

    def add_field(self, field, virtual=False):
        self.fields[field.name] = field

    def setup_pk(self, field):
        self.pk = field

    # required for admin.view.main.ChangeList.get_queryset
    def get_field(self, field_name):
        field = self.fields.get(field_name)
        if not field:
            raise FieldDoesNotExist('{field} not exist.'.format(field=field_name))
        return field

from __future__ import unicode_literals

import six

from django.apps import apps
from django.db import models

from .options import ThreadOptions
from .manager import ThreadManager

class ThreadBase(type):

    def __new__(cls, name, bases, attrs):
        cls = super(ThreadBase, cls).__new__(cls, name, bases, attrs)
        app_config = apps.get_containing_app_config(attrs['__module__'])
        if getattr(cls, "app_label", None) is None:
            attrs['_meta'].app_label = app_config.label
        attrs['_meta'].contribute_to_class(cls, '_meta')
        attrs['_default_manager'].contribute_to_class(cls, '_default_manager')

        for attr in attrs:
            if attr[0] != '_' and isinstance(attrs[attr], models.Field):
                try:
                    attrs[attr].contribute_to_class(cls, attr)
                except KeyError:
                    pass
        return cls
    
        
class Thread(object):
    __metaclass__ = ThreadBase
    _default_manager = ThreadManager()
    _meta = ThreadOptions()
    
    title = models.CharField(max_length=100)
    link = models.URLField()
    id = models.UUIDField(primary_key=True)
    forum = models.CharField(max_length=100)


    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _get_pk_val(self, meta=None):
        if not meta:
            meta = self._meta
        return getattr(self, meta.pk.attname)

    def _set_pk_val(self, value):
        return setattr(self, self._meta.pk.attname, value)

    pk = property(_get_pk_val, _set_pk_val)

    def __str__(self):
        return self.title
        
    def serializable_value(self, field_name):
        """
        Returns the value of the field name for this instance. If the field is
        a foreign key, returns the id value, instead of the object. If there's
        no Field object with this name on the model, the model attribute's
        value is returned directly.

        Used to serialize a field's value (in the serializer, or form output,
        for example). Normally, you would just access the attribute directly
        and not use this method.
        """
        try:
            field = self._meta.get_field(field_name)
        except FieldDoesNotExist:
            return getattr(self, field_name)
        return getattr(self, field.attname)
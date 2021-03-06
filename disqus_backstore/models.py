from __future__ import unicode_literals

from django.db import models

from .manager import ThreadManager, PostManager


class Thread(models.Model):
    _base_manager = ThreadManager()
    _default_manager = _base_manager
    objects = _default_manager

    forum = models.CharField(max_length=100)
    id = models.BigIntegerField(primary_key=True)
    is_closed = models.BooleanField()
    link = models.URLField()
    title = models.CharField(max_length=100)

    def delete(self, using=None, keep_parents=False):
        self.__class__._default_manager.delete(self)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.__class__._default_manager.update(self)

    def __eq__(self, rhs):
        if not isinstance(rhs, self.__class__):
            return False
        return self.id == rhs.id

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def __unicode__(self):
        return self.title


class Post(models.Model):
    _base_manager = PostManager()
    _default_manager = _base_manager
    objects = _default_manager

    forum = models.CharField(max_length=100)
    id = models.BigIntegerField(primary_key=True)
    is_approved = models.BooleanField()
    message = models.TextField(blank=True)
    thread = models.ForeignKey(Thread)

    def delete(self, using=None, keep_parents=False):
        self.__class__._default_manager.delete(self)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.__class__._default_manager.update(self)

    def __eq__(self, rhs):
        if not isinstance(rhs, self.__class__):
            return False
        return self.id == rhs.id

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def __unicode__(self):
        return self.message if self.message else "Empty message"

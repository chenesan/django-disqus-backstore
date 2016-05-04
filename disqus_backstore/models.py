from __future__ import unicode_literals

from django.db import models

from .manager import ThreadManager, PostManager


class Thread(models.Model):
    objects = ThreadManager()

    forum = models.CharField(max_length=100)
    id = models.BigIntegerField(primary_key=True)
    is_closed = models.BooleanField()
    is_deleted = models.BooleanField()
    link = models.URLField()
    title = models.CharField(max_length=100)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.__class__._default_manager._update(self)

    def __eq__(self, rhs):
        return self.id == rhs.id

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class Post(models.Model):
    objects = PostManager()

    forum = models.CharField(max_length=100)
    id = models.BigIntegerField(primary_key=True)
    is_approved = models.BooleanField()
    is_deleted = models.BooleanField()
    is_spam = models.BooleanField()
    message = models.TextField(blank=True)
    thread = models.ForeignKey(Thread)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        pass

    def __eq__(self, rhs):
        return self.id == rhs.id

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def __str__(self):
        return self.message if self.message else "Empty message"

    def __unicode__(self):
        return self.message if self.message else "Empty message"

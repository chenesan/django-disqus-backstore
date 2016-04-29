from django.db.models.manager import Manager
from .query import ThreadQuerySet, PostQuerySet


class ThreadManager(Manager.from_queryset(ThreadQuerySet)):
    pass


class PostManager(Manager.from_queryset(PostQuerySet)):
    pass

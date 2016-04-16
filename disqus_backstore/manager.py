from django.db.models.manager import BaseManager
from .query import ThreadQuerySet, PostQuerySet

class ThreadManager(BaseManager.from_queryset(ThreadQuerySet)):
    pass

class PostManager(BaseManager.from_queryset(PostQuerySet)):
    pass

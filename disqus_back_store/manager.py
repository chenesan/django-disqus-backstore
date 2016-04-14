from django.db.models.manager import BaseManager
from .query import ThreadQuerySet

class ThreadManager(BaseManager.from_queryset(ThreadQuerySet)):
    pass

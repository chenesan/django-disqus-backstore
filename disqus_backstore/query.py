"""
Most of the `disqus_backstore.query` module has
the same interface in django `QuerySet` class,
ex. the implementation of filter/get method.
"""

import copy

from django.db.models.query import BaseIterable

from .disqus_interface import DisqusQuery


class Query(object):
    def __init__(self, query_string, value, negate):
        self.query_string = query_string
        self.value = value
        self.negate = negate


def get_thread_from_thread_list(id, thread_list):
    for thread in thread_list:
        if str(thread.id) == id:
            return thread
    return None

def meet_querys(data, query_objs):
    for q in query_objs:
        if q.query_string == 'pk' or q.query_string == 'id':
            if q.negate and data['id'] == str(q.value):
                return False
            elif not q.negate and data['id'] != str(q.value):
                return False
        # It's a dirty workaround for thread delete view to filter Post
        # We should have a class to parse the filter string used in admin
        if q.query_string == 'thread__in':
            thread_ids = [str(obj.id) for obj in q.value]
            if q.negate and data['thread'] in thread_ids:
                return False
            elif not q.negate and data['thread'] not in thread_ids:
                return False
    return True


class ThreadIterable(BaseIterable):
    def __iter__(self):
        queryset = self.queryset
        #processing query string, currently only processing primary key
        rawdata = queryset.query.get_threads_list()
        for thread in rawdata['response']:
            if meet_querys(thread, queryset.query_objs):
                 obj = queryset.create(
                     id=int(thread.get('id')),
                     title=thread.get('title'),
                     link=thread.get('link'),
                     forum=thread.get('forum'),
                     is_deleted=thread.get('isDeleted'),
                     is_closed=thread.get('isClosed'),
                 )
        # Dirty hack for unique check in admin changeform view
                 obj._state.adding = False
                 yield obj


class PostIterable(BaseIterable):
    def __iter__(self):
        queryset = self.queryset
        #processing query string, currently only processing primary key
        rawdata = queryset.query.get_posts_list()
        #hack for reduce redundant thread list request
        thread_field = queryset.model._meta.get_field('thread')
        thread_list = list(thread_field.remote_field.model.objects.all())
        for post in rawdata['response']:
            if meet_querys(post, queryset.query_objs):
                thread = get_thread_from_thread_list(post['thread'], thread_list)
                obj = queryset.create(
                    id=int(post.get('id')),
                    forum=post.get('forum'),
                    is_approved=post.get('isApproved'),
                    is_deleted=post.get('isDeleted'),
                    is_spam=post.get('isSpam'),
                    message=post.get('raw_message'),
                    thread=thread,
                )
                obj._state.adding = False
                yield obj


class DisqusQuerySet(object):

    ##############
    #Magic Method#
    ##############
    def __init__(self, model=None, query=None, using=None, hints=None):
        self.model = model
        self.query = query or DisqusQuery()
        if using:
            self.using = using
        self._prefetch_related_lookups = []
        self.query_objs = []
        self._result_cache = None

    def __iter__(self):
        self._fetch_all()
        return iter(self._result_cache)

    def __getitem__(self, i):
        if self._result_cache is None:
            self._fetch_all()
        return self._result_cache[i]

    def __len__(self):
        if self._result_cache is None:
            self._fetch_all()
        return len(self._result_cache)

    # Private Method

    def _fetch_all(self):
        if self._result_cache is None:
            self._result_cache = list(self.iterator())

    def _clone(self, **kwargs):
        clone = self.__class__(model=self.model, query=self.query, using=self.using)
        clone.query_objs = self.query_objs
        return clone

    # Iterator factory
    def iterator(self):
        return self._iterable_class(self)

    # Create Model Instance
    def create(self, *args, **kwargs):
        obj = self.model(**kwargs)
        return obj

    # Public Method which sends request

    def count(self, *args, **kwargs):
        return len(self)

    def get(self, *args, **kwargs):
        clone = self.filter(*args, **kwargs)
        clone._fetch_all()
        if len(clone._result_cache) == 1:
            return clone._result_cache[0]
        elif len(clone._result_cache) == 0:
            return None
        else:
            raise clone.model.MultipleObjectsReturned(
                "get() returned more than one %s -- it returned %s!" %
                (self.model._meta.object_name, len(self._result_cache))
            )

    def exists(self):
        if self._result_cache is None:
            try:
                self.iterator().next()
            except StopIteration as e:
                return False
            return True
        return bool(self._result_cache)

    # Public method to add query, currently only support primary key

    def filter(self, *args, **kwargs):
        return self.filter_or_exclude(False, *args, **kwargs)

    def exclude(self, *args, **kwargs):
        return self.filter_or_exclude(True, *args, **kwargs)

    def filter_or_exclude(self, negate, *args, **kwargs):
        clone = self._clone()
        for k, v in kwargs.items():
            q = Query(k, v, negate=negate)
            clone.query_objs.append(q)
        return clone

    # Dumb Implementation

    def using(self, alias):
        clone = self._clone()
        clone._db = alias
        return clone

    def order_by(self, *args, **kwargs):
        return self._clone()

    def complex_filter(self, filter_obj):
        return self._clone()

    def all(self, *args, **kwargs):
        return self._clone()

    def select_related(self, *fields):
        return self._clone()


class ThreadQuerySet(DisqusQuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super(ThreadQuerySet, self).__init__(model, query, using, hints)
        self._iterable_class = ThreadIterable

    def delete(self, obj):
        self.query.delete_thread(obj.id)

    def update(self, new_instance):
        old_instance = self.get(id=new_instance.id)
        fields = self.model._meta.get_fields()
        for f in fields:
            attname = getattr(f, 'attname', None)
            if attname:
                old_val = getattr(old_instance, f.attname)
                new_val = getattr(new_instance, f.attname)
                if old_val != new_val:
                    update_func = getattr(self.query, 'change_thread_'+attname)
                    result = update_func(new_instance.id, old_val, new_val)


class PostQuerySet(DisqusQuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super(PostQuerySet, self).__init__(model, query, using, hints)
        self._iterable_class = PostIterable

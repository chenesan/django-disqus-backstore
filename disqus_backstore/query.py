import copy

from .disqus_interface import DisqusQuery


class DisqusQuerySet(object):
    def __init__(self, model=None, query=None, using=None, hints=None):
        self.model = model
        self.query = query or DisqusQuery()
        if using:
            self.using = using
        self.data = []
        self._prefetch_related_lookups = []

    def create(self, *args, **kwargs):
        obj = self.model(**kwargs)
        return obj

    def order_by(self, *args, **kwargs):
        return self

    def complex_filter(self, filter_obj):
        return self

    def all(self, *args, **kwargs):
        return self._clone()

    def count(self, *args, **kwargs):
        return len(self.data)

    def iterator(self):
        return iter(self.data)

    def using(self, alias):
        clone = self._clone()
        clone._db = alias
        return clone

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def _clone(self, **kwargs):
        clone = self.__class__()
        clone.data = copy.deepcopy(self.data)
        return clone

    def exists(self):
        print self.data
        return bool(self.data)

    def exclude(self, *args, **kwargs):
        pk = kwargs.pop('pk', None)
        if pk:
            for d in self.data:
                if d.id == pk:
                    self.data.remove(d)
        return self

class ThreadQuerySet(DisqusQuerySet):
    def get(self, *args, **kwargs):
        kwargs['thread'] = kwargs.pop('id', None)
        rawdata = self.query.get_threads_list(**kwargs)['response']
        if len(rawdata) > 2:
            raise self.model.MultipleObjectsReturned(
                "get() returned more than one %s -- it returned %s!" %
                (self.model._meta.object_name, len(rawdata))
            )
        elif len(rawdata) == 1:
            thread = rawdata[0]
            obj = self.create(
                id=int(thread.get('id')),
                title=thread.get('title'),
                link=thread.get('link'),
                forum=thread.get('forum'),
                is_deleted=thread.get('isDeleted'),
                is_closed=thread.get('isClosed'),
            )
            obj._state.adding = False
            self.data.append(obj)
            return obj

    def filter(self, *args, **kwargs):
        if not getattr(self, 'rawdata', None):
            rawdata = self.query.get_threads_list()
        self.data = [self.create(
            id=int(thread.get('id')),
            title=thread.get('title'),
            link=thread.get('link'),
            forum=thread.get('forum'),
            is_deleted=thread.get('isDeleted'),
            is_closed=thread.get('isClosed'),
        ) for thread in rawdata['response']]
        # Dirty hack for unique check in admin changeform view
        for obj in self.data:
            obj._state.adding = False
        pk = kwargs.pop('id', None)
        if pk:
            for thread in self.data:
                if thread.id == pk:
                    self.data = [thread]
                    break
            if self.data[0].id != pk:
                self.data = []
        return self

    def _update(self, new_instance):
        old_instance = self.get(id=new_instance.id)
        fields = self.model._meta.get_fields()
        print fields
        for f in fields:
            attname = getattr(f, 'attname', None)
            if attname:
                old_val = getattr(old_instance, f.attname)
                new_val = getattr(new_instance, f.attname)
                if old_val != new_val:
                    update_func = getattr(self.query, 'change_thread_'+attname)
                    result = update_func(new_instance.id, old_val, new_val)
                    print result

class PostQuerySet(DisqusQuerySet):
    def get(self, *args, **kwargs):
        """
        Because there's no "post" argument in diqus fourm/listPost API
        (But there's "thread" argument in forum/listThread API!),
        we have to use posts/details API to get single post..
        """
        post_id = kwargs.pop('id')
        post = self.query.get_post(post_id, **kwargs)['response']
        thread_field = self.model._meta.get_field('thread')
        thread = thread_field.remote_field.model.objects.get(id=post['thread'])
        obj = self.create(
            id=int(post.get('id')),
            forum=post.get('forum'),
            is_approved=post.get('isApproved'),
            is_deleted=post.get('isDeleted'),
            is_spam=post.get('isSpam'),
            message=post.get('raw_message'),
            thread=thread,
        )
        obj._state.adding = False
        self.data.append(obj)
        return obj

    def filter(self, *args, **kwargs):
        if not getattr(self, 'rawdata', None):
            rawdata = self.query.get_posts_list()
        for post in rawdata['response']:
            thread_field = self.model._meta.get_field('thread')
            thread = thread_field.remote_field.model.objects.get(id=post['thread'])
            obj = self.create(
                id=int(post.get('id')),
                forum=post.get('forum'),
                is_approved=post.get('isApproved'),
                is_deleted=post.get('isDeleted'),
                is_spam=post.get('isSpam'),
                message=post.get('raw_message'),
                thread=thread,
            )
            self.data.append(obj)
        # Dirty hack for admin.changeform_view
        for obj in self.data:
            obj._state.adding = False
        pk = kwargs.pop('id', None)
        if pk:
            for thread in self.data:
                if thread.id == pk:
                    self.data = [thread]
                    break
            if self.data[0].id != pk:
                self.data = []
        return self

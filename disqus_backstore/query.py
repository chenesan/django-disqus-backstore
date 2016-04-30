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


class ThreadQuerySet(DisqusQuerySet):
    def get(self, *args, **kwargs):
        kwargs['thread'] = kwargs.pop('id')
        rawdata = self.query.get_threads_list(**kwargs)['response']
        if len(rawdata) > 2:
            raise self.model.MultipleObjectsReturned(
                "get() returned more than one %s -- it returned %s!" %
                (self.model._meta.object_name, len(rawdata))
            )
        elif len(rawdata) == 1:
            thread = rawdata[0]
            return self.create(
                id=int(thread.get('id')),
                title=thread.get('title'),
                link=thread.get('link'),
                forum=thread.get('forum'),
                is_deleted=thread.get('isDeleted'),
                is_closed=thread.get('isClosed'),
                is_spam=thread.get('isSpam'),
            )

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
            is_spam=thread.get('isSpam'),
        ) for thread in rawdata['response']]
        return self


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
        return self.create(
            id=int(post.get('id')),
            forum=post.get('forum'),
            is_approved=post.get('isApproved'),
            is_deleted=post.get('isDeleted'),
            is_spam=post.get('isSpam'),
            message=post.get('raw_message'),
            thread=thread,
        )

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
        return self

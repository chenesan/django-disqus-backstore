import copy

from .disqus_interface import DisqusQuery


class ThreadQuerySet(object):
    # order_by, filter, query are required in admin.options.get_queryset
    def __init__(self, model=None, query=None, using=None, hints=None):
        self.model = model
        self.query = query or DisqusQuery()
        self.using = using

    def create(self, *args, **kwargs):
        obj = self.model(**kwargs)
        return obj

    def order_by(self, *args, **kwargs):
        return self

    def get(self, *args, **kwargs):
        params = dict()
        for k, v in kwargs.items():
            if k == 'id':
                params['thread'] = v
            else:
                params[k] = v
        rawdata = self.query.get_threads_list(**params)['response']
        if len(rawdata) > 2:
            raise(RuntimeError, "There are more than two objects.")
        elif len(rawdata) == 1:
            thread = rawdata[0]
            return self.create(
                id=int(thread['id']),
                title=thread['title'],
                link=thread['link'],
                forum=thread['forum']
            )

    # TODO: Currently for prove of concept, we just get data
    # from disqus api and put them directly into model instance.
    # We should seperate the model instance generation code elsewhere
    def filter(self, *args, **kwargs):
        if not getattr(self,'rawdata',None):
            self.rawdata = self.query.get_threads_list()
        self.data = [self.create(
            id=int(thread['id']),
            title=thread['title'],
            link=thread['link'],
            forum=thread['forum']
        ) for thread in self.rawdata['response']]
        return self

    def all(self, *args, **kwargs):
        return self.data

    def count(self, *args, **kwargs):
        return len(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def _clone(self, **kwargs):
        clone = ThreadQuerySet()
        clone.rawdata = copy.deepcopy(self.rawdata)
        clone.data = copy.deepcopy(self.data)
        return clone

class PostQuerySet(object):
    # order_by, filter, query are required in admin.options.get_queryset
    def __init__(self, model=None, query=None, using=None, hints=None):
        self.model = model
        self.query = query or DisqusQuery()
        self.using = using

    def create(self, *args, **kwargs):
        obj = self.model(**kwargs)
        return obj

    def order_by(self, *args, **kwargs):
        return self

    # TODO: Currently for prove of concept, we just get data
    # from disqus api and put them directly into model instance.
    # We should seperate the model instance generation code elsewhere
    def filter(self, *args, **kwargs):
        if not getattr(self,'rawdata',None):
            self.rawdata = self.query.get_posts_list()
        self.data = [self.create(
            id=int(post['id']),
            is_spam=post['isSpam'],
            is_deleted=post['isDeleted'],
            is_approved=post['isApproved'],
            message=post['raw_message'],
            forum=post['forum'],
            thread=int(post['thread'])
        ) for post in self.rawdata['response']]
        return self

    def all(self, *args, **kwargs):
        return self.data

    def count(self, *args, **kwargs):
        return len(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def _clone(self, **kwargs):
        clone = PostQuerySet()
        clone.rawdata = copy.deepcopy(self.rawdata)
        clone.data = copy.deepcopy(self.data)
        return clone
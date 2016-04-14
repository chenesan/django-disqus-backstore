import copy

from .disqus_interface import DisqusQuery


#QuerySet, should be properly defined
class ThreadQuerySet(object):
    # order_by, filter, query are required in admin.options.get_queryset
    def __init__(self, model=None, query=None, using=None, hints=None):
        self.model = model
        self.query = query or DisqusQuery()
        self.using = using
        #dumb implementation for queryset data, should be replaced by disqus api

    def create(self, *args, **kwargs):
        obj = self.model(**kwargs)
        return obj
        
    def order_by(self, *args, **kwargs):
        return self
    # admin needs filter to get current model data
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
    # To support count operation, queryset should has __len__
    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def _clone(self, **kwargs):
        clone = ThreadQuerySet()
        clone.rawdata = copy.deepcopy(self.rawdata)
        clone.data = copy.deepcopy(self.data)
        return clone
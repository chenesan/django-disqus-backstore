from django.utils import timezone

class QueryNotRegistered(Exception):
    pass


class CacheRegistry(object):
    """
    It's a utility class to register category of DISQUS query API.
    Because we don't want to call multiple times in `Thread/Post.get()`
    when we don't update/delete anything. For each cache we use a
    `cache_record` attribute to save the call history.
    Once updating/deletion operation occur, the following `cache_clearer`
    decorator will ask this class to clear the corresponding query API caches.
    """
    def __init__(self):
        # query_category -> set of related query cache
        self.query_categories = dict()

    def register(self, category, query_cache):
        if category not in self.query_categories:
            self.query_categories[category] = set()
        self.query_categories[category].add(query_cache)

    def clear(self, query_cache_category):
        try:
            for cache in self.query_categories[query_cache_category]:
                cache.clear()
        except KeyError:
            raise QueryNotRegistered("Category {category} isn't registered.".format(category=query_cache_category))


cache_registry = CacheRegistry()


def cache_clearer(query_categories):
    class CacheClearer(object):
        def __init__(self, func, *args, **kwargs):
            self.func = func
            self.query_categories = query_categories

        def __call__(self, *args, **kwargs):
            result = self.func(*args, **kwargs)
            for query_category in self.query_categories:
                cache_registry.clear(query_category)
            return result

        def __get__(self, instance, owner):
            def f(*args, **kwargs):
                return self(instance, *args, **kwargs)
            return f


    return CacheClearer

class QueryRecord(object):
    def __init__(self, result, refreshed_seconds):
        self.result = result
        self.timestamp = timezone.now()
        self.refreshed_seconds = refreshed_seconds

    def is_outdated(self, thres_seconds=None):
        if thres_seconds is None:
            thres_seconds = self.refreshed_seconds
        time_delta = timezone.now() - self.timestamp
        return time_delta.seconds > thres_seconds

def query_cache(category, refreshed_seconds=5):
    """
    A decorator for caching query API result.
    For each call we use the arguments as key.
    if key is not in the cache, save the result,
    else just used the previous result.
    It's' registered in `cache_registry` class. And write operations
    with `cache_clearer` decorator can get the registry. Once writing
    operation occurs, `cache_clearer` will ask `cache_registry` to
    clear the corresponding cache.
    """
    class QueryCache(object):
        def __init__(self, func):
            self.call_record = dict()
            self.func = func
            self.name = getattr(func, 'name', func.__name__)
            self.refreshed_seconds = refreshed_seconds
            cache_registry.register(category, self)

        def __call__(self, *args, **kwargs):
            args_record = tuple(args)
            kwargs_record = tuple(kwargs.items())
            all_args = (args_record, kwargs_record)
            record = self.call_record.get(all_args, None)
            if record and not record.is_outdated():
                return record.result
            else:
                result = self.func(*args, **kwargs)
                self.call_record[all_args] = QueryRecord(result, self.refreshed_seconds)
                return result

        def __get__(self, instance, owner):
            def f(*args, **kwargs):
                return self(instance, *args, **kwargs)
            return f

        def clear(self):
            self.call_record = dict()

    return QueryCache

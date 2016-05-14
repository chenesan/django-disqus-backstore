import sys

import requests

from django.conf import settings

from .utils import cache_clearer, query_cache

class RequestError(Exception):
    pass


class DISQUSAPIError(Exception):
    pass


def send_request_to_disqus(model_name, method_name, header, params):
    api_template = 'https://disqus.com/api/3.0/{model_name}/{method_name}.json'
    api_url = api_template.format(model_name=model_name, method_name=method_name)
    try:
        if header == "get":
            response = requests.get(api_url, params=params).json()
        elif header == "post":
            response = requests.post(api_url, params=params).json()
        else:
            raise RequestError("We can't handle header {header}".format(header=header))
    except:
        e = sys.exc_info()[0]
        raise RequestError(e)
    else:
        if response["code"] != 0:
            # Error occur, just raise exception with response message
            raise DISQUSAPIError(response["response"])
        else:
            return response

class DisqusQuery(object):
    select_related = False
    order_by = []
    public_key = getattr(settings, "DISQUS_PUBLIC_KEY")
    secret_key = getattr(settings, "DISQUS_SECRET_KEY")
    forum = getattr(settings, "DISQUS_FORUM_SHORTNAME")
    access_token = getattr(settings, "DISQUS_ACCESS_TOKEN")

    @query_cache('thread')
    def get_threads_list(self, *args, **kwargs):
        model_name = "forums"
        method_name = "listThreads"
        params = {
            'api_secret': self.secret_key,
            'forum': self.forum,
            'limit': 100,
        }
        header = "get"
        params.update(kwargs)
        return send_request_to_disqus(model_name, method_name, header, params)

    @query_cache('post')
    def get_posts_list(self, thread_id=None, **kwargs):
        params = {
            'api_secret': self.secret_key,
            'forum': self.forum,
            'include': [
                "unapproved",
                "approved",
                "spam",
                "flagged",
                "highlighted"
            ],
        }
        if thread_id:
            params['thread'] = thread_id
            model_name = "threads"
            method_name = "listPosts"
            header = "get"
            return send_request_to_disqus(model_name, method_name, header, params)
        else:
            params['forum'] = self.forum
            model_name = "forums"
            method_name = "listPosts"
            header = "get"
            return send_request_to_disqus(model_name, method_name, header, params)

    @query_cache('thread')
    def get_thread(self, thread_id, *args, **kwargs):
        model_name = "threads"
        method_name = "details"
        header = "get"
        params = {
            'api_secret': self.secret_key,
            'thread': thread_id
        }
        return send_request_to_disqus(model_name, method_name, header, params)

    @query_cache('post')
    def get_post(self, post_id, *args, **kwargs):
        model_name = "posts"
        method_name = "details"
        header = "get"
        params = {
            'api_secret': self.secret_key,
            'post': post_id
        }
        return send_request_to_disqus(model_name, method_name, header, params)

    def change_thread_is_closed(self, thread_id, old_val, new_val):
        assert old_val != new_val
        if old_val:
            return self.open_thread(thread_id)
        else:
            return self.close_thread(thread_id)

    @cache_clearer(['thread'])
    def open_thread(self, thread_id):
        model_name = 'threads'
        method_name = 'open'
        header = "post"
        params = {
            'api_secret': self.secret_key,
            'thread': thread_id,
            'access_token': self.access_token
        }
        return send_request_to_disqus(model_name, method_name, header, params)

    @cache_clearer(['thread'])
    def close_thread(self, thread_id):
        model_name = 'threads'
        method_name = 'close'
        header = "post"
        params = {
            'api_secret': self.secret_key,
            'thread': thread_id,
            'access_token': self.access_token
        }
        return send_request_to_disqus(model_name, method_name, header, params)

    @cache_clearer(['thread', 'post'])
    def delete_thread(self, thread_id):
        model_name = 'threads'
        method_name = 'remove'
        header = "post"
        params = {
            'api_secret': self.secret_key,
            'thread': thread_id,
            'access_token': self.access_token
        }
        return send_request_to_disqus(model_name, method_name, header, params)

    @cache_clearer(['post'])
    def delete_post(self, post_id):
        model_name = 'posts'
        method_name = 'remove'
        header = "post"
        params = {
            'api_secret': self.secret_key,
            'post': post_id,
            'access_token': self.access_token
        }
        return send_request_to_disqus(model_name, method_name, header, params)

    @cache_clearer(['thread', 'post'])
    def delete_threads(self, thread_ids):
        # thread_ids must be a list of thread id
        model_name = 'threads'
        method_name = 'remove'
        header = "post"
        params = {
            'api_secret': self.secret_key,
            'thread': thread_ids,
            'access_token': self.access_token
        }
        return send_request_to_disqus(model_name, method_name, header, params)

    @cache_clearer(['post'])
    def delete_posts(self, post_ids):
        # post_ids must be a list of post id
        model_name = 'posts'
        method_name = 'remove'
        header = "post"
        params = {
            'api_secret': self.secret_key,
            'post': post_ids,
            'access_token': self.access_token
        }
        return send_request_to_disqus(model_name, method_name, header, params)

    @cache_clearer(['thread'])
    def recover_thread(self, thread_id):
        model_name = 'threads'
        method_name = 'restore'
        header = "post"
        params = {
            'api_secret': self.secret_key,
            'thread': thread_id,
            'access_token': self.access_token
        }
        return send_request_to_disqus(model_name, method_name, header, params)

    def change_post_is_approved(self, post_id, old_val, new_val):
        assert old_val != new_val
        if old_val:
            return self.spam_post(post_id)
        else:
            return self.approve_post(post_id)

    @cache_clearer(['post'])
    def approve_post(self, post_id):
        model_name = 'posts'
        method_name = 'approve'
        header = "post"
        params = {
            'api_secret': self.secret_key,
            'post': post_id,
            'access_token': self.access_token
        }
        return send_request_to_disqus(model_name, method_name, header, params)


    @cache_clearer(['post'])
    def spam_post(self, post_id):
        model_name = 'posts'
        method_name = 'spam'
        header = "post"
        params = {
            'api_secret': self.secret_key,
            'post': post_id,
            'access_token': self.access_token
        }
        return send_request_to_disqus(model_name, method_name, header, params)

    @cache_clearer(['post'])
    def change_post_message(self, post_id, old_val, new_val):
        model_name = 'posts'
        method_name = 'update'
        header = "post"
        params = {
            'api_secret': self.secret_key,
            'post': post_id,
            'message': new_val,
            'access_token': self.access_token
        }
        return send_request_to_disqus(model_name, method_name, header, params)

disqus_query = DisqusQuery()

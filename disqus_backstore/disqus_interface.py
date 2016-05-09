import requests
from django.conf import settings


class DisqusQuery(object):
    select_related = False
    order_by = []
    public_key = getattr(settings, "DISQUS_PUBLIC_KEY")
    secret_key = getattr(settings, "DISQUS_SECRET_KEY")
    forum = getattr(settings, "DISQUS_FORUM_SHORTNAME")
    access_token = getattr(settings, "DISQUS_ACCESS_TOKEN")

    def get_threads_list(self, *args, **kwargs):
        params = {
            'api_secret': self.secret_key,
            'forum': self.forum,
            'limit': 100,
        }
        params.update(kwargs)
        return requests.get('https://disqus.com/api/3.0/forums/listThreads.json',
                            params=params).json()

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
            return requests.get('https://disqus.com/api/3.0/threads/listPosts.json',
                                params=params).json()
        else:
            params['forum'] = self.forum
            return requests.get('https://disqus.com/api/3.0/forums/listPosts.json',
                                params=params).json()

    def get_thread(self, thread_id, *args, **kwargs):
        return requests.get('https://disqus.com/api/3.0/threads/details.json',
                            params={
                                'api_secret': self.secret_key,
                                'thread': thread_id
                            }).json()

    def get_post(self, post_id, *args, **kwargs):
        return requests.get('https://disqus.com/api/3.0/posts/details.json',
                            params={
                                'api_secret': self.secret_key,
                                'post': post_id
                            }).json()

    def change_thread_is_closed(self, thread_id, old_val, new_val):
        assert old_val != new_val
        if old_val:
            return self.open_thread(thread_id)
        else:
            return self.close_thread(thread_id)

    def open_thread(self, thread_id):
        return requests.post('https://disqus.com/api/3.0/threads/open.json',
                            params={
                                'api_secret': self.secret_key,
                                'thread': thread_id,
                                'access_token': self.access_token
                            }).json()

    def close_thread(self, thread_id):
        return requests.post('https://disqus.com/api/3.0/threads/close.json',
                             params={
                                 'api_secret': self.secret_key,
                                 'thread': thread_id,
                                 'access_token': self.access_token
                             }).json()

    def delete_thread(self, thread_id):
        return requests.post('https://disqus.com/api/3.0/threads/remove.json',
                            params={
                                'api_secret': self.secret_key,
                                'thread': thread_id,
                                'access_token': self.access_token
                            }).json()

    def delete_post(self, post_id):
        return requests.post('https://disqus.com/api/3.0/posts/remove.json',
                            params={
                                'api_secret': self.secret_key,
                                'post': post_id,
                                'access_token': self.access_token
                            }).json()

    def delete_threads(self, thread_ids):
        # thread_ids must be a list of thread id
        return requests.post('https://disqus.com/api/3.0/threads/remove.json',
                            params={
                                'api_secret': self.secret_key,
                                'thread': thread_ids,
                                'access_token': self.access_token
                            }).json()

    def delete_posts(self, post_ids):
        # post_ids must be a list of post id
        return requests.post('https://disqus.com/api/3.0/posts/remove.json',
                            params={
                                'api_secret': self.secret_key,
                                'post': post_ids,
                                'access_token': self.access_token
                            }).json()

    def recover_thread(self, thread_id):
        return requests.post('https://disqus.com/api/3.0/threads/restore.json',
                             params={
                                 'api_secret': self.secret_key,
                                 'thread': thread_id,
                                 'access_token': self.access_token
                             }).json()

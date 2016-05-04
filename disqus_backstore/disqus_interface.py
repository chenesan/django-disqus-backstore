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

    def get_posts_list(self, *args, **kwargs):
        return requests.get('https://disqus.com/api/3.0/forums/listPosts.json',
                            params={
                                'api_secret': self.secret_key,
                                'forum': self.forum,
                                'include': [
                                    "unapproved",
                                    "approved",
                                    "spam",
                                    "deleted",
                                    "flagged",
                                    "highlighted"
                                ],
                            }).json()
    def get_thread(self, thread, *args, **kwargs):
        return requests.get('https://disqus.com/api/3.0/threads/details.json',
                            params={
                                'api_secret': self.secret_key,
                                'thread': thread
                            }).json()

    def get_post(self, post, *args, **kwargs):
        return requests.get('https://disqus.com/api/3.0/posts/details.json',
                            params={
                                'api_secret': self.secret_key,
                                'post': post
                            }).json()

    def change_thread_is_closed(self, thread, old_val, new_val):
        assert old_val != new_val
        if old_val:
            return self.open_thread(thread)
        else:
            return self.close_thread(thread)

    def open_thread(self, thread):
        return requests.post('https://disqus.com/api/3.0/threads/open.json',
                            params={
                                'api_secret': self.secret_key,
                                'thread': thread,
                                'access_token': self.access_token
                            }).json()

    def close_thread(self, thread):
        return requests.post('https://disqus.com/api/3.0/threads/close.json',
                             params={
                                 'api_secret': self.secret_key,
                                 'thread': thread,
                                 'access_token': self.access_token
                             }).json()

    def delete_thread(self, thread):
        return requests.post('https://disqus.com/api/3.0/threads/remove.json',
                            params={
                                'api_secret': self.secret_key,
                                'thread': thread,
                                'access_token': self.access_token
                            }).json()

    def recover_thread(self, thread):
        return requests.post('https://disqus.com/api/3.0/threads/restore.json',
                             params={
                                 'api_secret': self.secret_key,
                                 'thread': thread,
                                 'access_token': self.access_token
                             }).json()

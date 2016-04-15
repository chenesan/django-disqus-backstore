import requests
from django.conf import settings


# Needed in admin.main.get_queryset
class DisqusQuery(object):
    select_related = False
    order_by = []
    secret_key = getattr(settings, "DISQUS_SECRET_KEY")
    forum = getattr(settings, "DISQUS_FORUM_SHORTNAME")
    
    def get_threads_list(self):
        return requests.get('https://disqus.com/api/3.0/forums/listThreads.json',
                            params={
                                'api_secret': self.secret_key,
                                'forum': self.forum
                            }).json()

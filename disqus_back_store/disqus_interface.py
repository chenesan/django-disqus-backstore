from django.conf import settings
import requests

secret_key = getattr(settings, "DISQUS_SECRET_KEY")

print 'secret',secret_key

# Needed in admin.main.get_queryset
class DisqusQuery(object):
    # not sure why the admin.main.get_queryset need select_related
    select_related = False
    # required for admin.main.get_queryset to get ordering field
    order_by = []

    def get_threads_list(self):
        return requests.get('https://disqus.com/api/3.0/forums/listThreads.json',params={
            'api_secret': secret_key,
            'forum': 'wwwloperuvcom'
        }).json()

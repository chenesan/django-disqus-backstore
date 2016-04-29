import json
import os

import mock

from django.test import TestCase

from .models import Thread
from disqus_interface import DisqusQuery


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')
THREADS_TEST_DATA = json.load(open(os.path.join(TEST_DATA_DIR, 'threads_list.json'), 'r'))
POST_TEST_DATA = json.load(open(os.path.join(TEST_DATA_DIR, 'posts_list.json'), 'r'))


class DisqusThreadAdminTest(TestCase):

    def test_thread_model_in_change_list_view(self):
        response = self.client.get('/admin/disqus_backstore/thread/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_post_model_in_change_list_view(self):
        response = self.client.get('/admin/disqus_backstore/post/', follow=True)
        self.assertEqual(response.status_code, 200)


class DisqusThreadQuerySetTest(TestCase):

    def test_thread_queryset_get(self):
        with mock.patch.object(DisqusQuery, 'get_threads_list', return_value=THREADS_TEST_DATA):
            all_qs = Thread.objects.filter()

        obj = all_qs[0]
        with mock.patch.object(DisqusQuery, 'get_threads_list', return_value={
                'response': [THREADS_TEST_DATA['response'][0]]
        }):
            self.assertEqual(obj, Thread.objects.get(id=obj.id))

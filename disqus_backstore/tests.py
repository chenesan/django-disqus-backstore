import json
import os

import mock

from django.contrib import admin
from django.test import TestCase, RequestFactory

from .admin import ThreadAdmin, PostAdmin
from .models import Thread, Post
from disqus_interface import DisqusQuery


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')
THREADS_LIST_RESPONSE = json.load(open(os.path.join(TEST_DATA_DIR, 'threads_list.json'), 'r'))
POSTS_LIST_RESPONSE = json.load(open(os.path.join(TEST_DATA_DIR, 'posts_list.json'), 'r'))
POST_DETAIL_RESPONSE = json.load(open(os.path.join(TEST_DATA_DIR, 'post_detail.json'), 'r'))
SINGLE_THREAD_LIST_RESPONSE =  json.load(open(os.path.join(TEST_DATA_DIR, 'single_thread_list.json'), 'r'))

class MockSuperUser(object):
    is_active = True
    is_staff = True

    def has_perm(self, perm):
        return True

    def has_module_perms(self, app_label):
        return True


class DisqusAdminTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_thread_model_in_change_list_view(self):
        response = self.client.get('/admin/disqus_backstore/thread/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_post_model_in_change_list_view(self):
        response = self.client.get('/admin/disqus_backstore/post/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_thread_model_in_change_form_view(self):
        with mock.patch.object(DisqusQuery, 'get_threads_list', return_value=SINGLE_THREAD_LIST_RESPONSE):
            thread_id = SINGLE_THREAD_LIST_RESPONSE['response'][0]['id']
            thread = DisqusQuery().get_threads_list(thread=thread_id)['response'][0]
            Thread.objects.create(
                id=int(thread.get('id')),
                forum=thread.get('forum'),
                is_closed=thread.get('isClosed'),
                is_deleted=thread.get('isDeleted'),
                is_spam=thread.get('isSpam'),
                title=thread.get('title'),
            )
            request = self.factory.get('/admin/disqus_backstore/thread/{id}/change/'.format(id=thread_id), follow=True)
            request.user = MockSuperUser()
            response = ThreadAdmin(Thread, admin.site).change_view(request, thread_id)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("admin/change_form.html" in response.template_name)

    def test_post_model_in_change_form_view(self):
        with mock.patch.object(DisqusQuery, 'get_post', return_value=POST_DETAIL_RESPONSE):
            post_id = POST_DETAIL_RESPONSE['response']['id']
            post = DisqusQuery().get_post(post_id)['response']
            Post.objects.create(
                id=int(post.get('id')),
                forum=post.get('forum'),
                is_approved=post.get('isApproved'),
                is_deleted=post.get('isDeleted'),
                is_spam=post.get('isSpam'),
                message=post.get('raw_message'),
            )
            request = self.factory.get('/admin/disqus_backstore/post/2626306299/change/', follow=True)
            request.user = MockSuperUser()
            response = PostAdmin(Post, admin.site).change_view(request, post['id'])
            self.assertEqual(response.status_code, 200)
            self.assertTrue("admin/change_form.html" in response.template_name)

class DisqusThreadQuerySetTest(TestCase):

    def test_thread_queryset_get(self):
        with mock.patch.object(DisqusQuery, 'get_threads_list', return_value=THREADS_LIST_RESPONSE):
            all_qs = Thread.objects.filter()

        obj = all_qs[0]
        with mock.patch.object(DisqusQuery, 'get_threads_list', return_value={
                'response': [THREADS_LIST_RESPONSE['response'][0]]
        }):
            self.assertEqual(obj, Thread.objects.get(id=obj.id))

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

def thread_factory(thread_data):
    thread = Thread.objects.create(
        id=int(thread_data.get('id')),
        forum=thread_data.get('forum'),
        is_closed=thread_data.get('isClosed'),
        is_deleted=thread_data.get('isDeleted'),
        title=thread_data.get('title'),
    )
    return thread

def post_factory(post_data):
    post = Post.objects.create(
        id=int(post_data.get('id')),
        forum=post_data.get('forum'),
        is_approved=post_data.get('isApproved'),
        is_deleted=post_data.get('isDeleted'),
        is_spam=post_data.get('isSpam'),
        message=post_data.get('raw_message'),
    )
    return post

class MockSuperUser(object):
    is_active = True
    is_staff = True

    def has_perm(self, perm):
        return True

    def has_module_perms(self, app_label):
        return True


class DisqusAdminTest(TestCase):

    def test_thread_change_list_view__normal_case__correct_template_response(self):
        with mock.patch.object(DisqusQuery, 'get_threads_list', return_value=THREADS_LIST_RESPONSE):
            request = RequestFactory().get('/admin/disqus_backstore/thread/', follow=True)
            request.user = MockSuperUser()

            response = ThreadAdmin(Thread, admin.site).changelist_view(request)

            # what to test:
            # 1. template is admin/change_list.html and its subclass template
            # 2. status code 200
            # 3. thread objects == response
            # They should be tested together

            # All objects
            qs = Thread.objects.filter()
            template_names = set([
                'admin/change_list.html',
                'admin/disqus_backstore/change_list.html',
                'admin/disqus_backstore/thread/change_list.html',
            ])

            self.assertEqual(response.status_code, 200)
            self.assertEqual(set(response.template_name), template_names)
            self.assertEqual(response.context_data['cl'].result_list, qs)

    def test_post_change_list_view__normal_case__correct_template_response(self):
        with mock.patch.object(DisqusQuery, 'get_posts_list', return_value=POSTS_LIST_RESPONSE):
            request = RequestFactory().get('/admin/disqus_backstore/post/', follow=True)
            request.user = MockSuperUser()

            response = PostAdmin(Post, admin.site).changelist_view(request)

            # what to test:
            # 1. template is admin/change_list.html and its subclass template
            # 2. status code 200
            # 3. thread objects == response
            # They should be tested together

            # All objects
            qs = Post.objects.filter()
            template_names = set([
                'admin/change_list.html',
                'admin/disqus_backstore/change_list.html',
                'admin/disqus_backstore/post/change_list.html',
            ])

            self.assertEqual(response.status_code, 200)
            self.assertEqual(set(response.template_name), template_names)
            self.assertEqual(response.context_data['cl'].result_list, qs)

    def test_thread_change_form_view__normal_case__correct_template_response(self):
        with mock.patch.object(DisqusQuery, 'get_threads_list', return_value=SINGLE_THREAD_LIST_RESPONSE):
            thread_data = SINGLE_THREAD_LIST_RESPONSE['response'][0]
            thread_object = thread_factory(thread_data)
            request = RequestFactory().get('/admin/disqus_backstore/thread/{id}/change/'.format(id=thread_object.id), follow=True)
            request.user = MockSuperUser()

            response = ThreadAdmin(Thread, admin.site).change_view(request, thread_data['id'])
            # what to test:
            # 1. template is admin/change_form.html and its subclass template
            # 2. status code 200
            # 3. thread object id is equal to the form bounded value
            # (So they are the same one.)
            # They should be tested together

            # All objects
            template_names = set([
                'admin/change_form.html',
                'admin/disqus_backstore/change_form.html',
                'admin/disqus_backstore/thread/change_form.html',
            ])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(set(response.template_name), template_names)
            self.assertEqual(
                response.context_data['adminform'].form['id'].value(),
                thread_object.id
            )

    def test_post_change_form_view__normal_case__correct_template_response(self):
        with mock.patch.object(DisqusQuery, 'get_post', return_value=POST_DETAIL_RESPONSE):
            post_data = POST_DETAIL_RESPONSE['response']
            post_object = post_factory(post_data)
            request = RequestFactory().get('/admin/disqus_backstore/post/{id}/change/'.format(id=post_object.id), follow=True)
            request.user = MockSuperUser()

            response = PostAdmin(Post, admin.site).change_view(request, post_data['id'])
            template_names = set([
                'admin/change_form.html',
                'admin/disqus_backstore/change_form.html',
                'admin/disqus_backstore/post/change_form.html',
            ])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(set(response.template_name), template_names)
            self.assertEqual(
                response.context_data['adminform'].form['id'].value(),
                post_object.id
            )


class DisqusThreadQuerySetTest(TestCase):

    def test_get__normal_case__get_object_successfully(self):
        thread_data = THREADS_LIST_RESPONSE['response'][0]
        thread_id = int(thread_data.get('id'))
        with mock.patch.object(DisqusQuery, 'get_threads_list', return_value={
                'response': [thread_data,]
        }):
            obj = Thread.objects.get(id=thread_id)
            self.assertEqual(obj.id, thread_id)

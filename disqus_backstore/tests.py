from __future__ import unicode_literals

import json
import os

import mock

from django.contrib import admin
from django.contrib.admin.utils import quote
from django.contrib.auth import get_permission_codename
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import capfirst

from .admin import ThreadAdmin, PostAdmin
from .models import Thread, Post
from disqus_interface import DisqusQuery


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_data')
THREADS_LIST_RESPONSE = json.load(open(os.path.join(TEST_DATA_DIR, 'threads_list.json'), 'r'))
POSTS_LIST_RESPONSE = json.load(open(os.path.join(TEST_DATA_DIR, 'posts_list.json'), 'r'))
POST_DETAIL_RESPONSE = json.load(open(os.path.join(TEST_DATA_DIR, 'post_detail.json'), 'r'))
SINGLE_THREAD_LIST_RESPONSE =  json.load(open(os.path.join(TEST_DATA_DIR, 'single_thread_list.json'), 'r'))

def get_perm(Model, perm):
    """Return the permission object, for the Model"""
    ct = ContentType.objects.get_for_model(Model)
    return Permission.objects.get(content_type=ct, codename=perm)

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

    @mock.patch.object(DisqusQuery, 'get_threads_list', return_value=THREADS_LIST_RESPONSE)
    def test_thread_change_list_view__normal_case__correct_template_response(self, _):

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
        self.assertEqual(list(response.context_data['cl'].result_list), list(qs))

    @mock.patch.object(DisqusQuery, 'get_threads_list', return_value=THREADS_LIST_RESPONSE)
    @mock.patch.object(DisqusQuery, 'get_posts_list', return_value=POSTS_LIST_RESPONSE)
    def test_post_change_list_view__normal_case__correct_template_response(self, _, __):

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
        self.assertEqual(list(response.context_data['cl'].result_list), list(qs))

    @mock.patch.object(DisqusQuery, 'get_threads_list', return_value=SINGLE_THREAD_LIST_RESPONSE)
    def test_thread_change_form_view__normal_case__correct_template_response(self, _):
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

    @mock.patch.object(DisqusQuery, 'get_threads_list', return_value=THREADS_LIST_RESPONSE)
    @mock.patch.object(DisqusQuery, 'get_posts_list', return_value=POSTS_LIST_RESPONSE)
    def test_post_change_form_view__normal_case__correct_template_response(self, _, __):
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

    @mock.patch.object(DisqusQuery, 'get_threads_list', return_value=THREADS_LIST_RESPONSE)
    @mock.patch.object(DisqusQuery, 'get_posts_list', return_value=POSTS_LIST_RESPONSE)
    def test_thread_delete_view__get__success(self, _, __):
        thread_data = THREADS_LIST_RESPONSE['response'][0]
        post_data = POSTS_LIST_RESPONSE['response'][0]
        thread_object = thread_factory(thread_data)
        related_post_object = post_factory(post_data)
        related_post_object.thread = thread_object
        request = RequestFactory().get('/admin/disqus_backstore/thread/{id}/delete/'.format(id=thread_object.id), follow=True)
        request.user = MockSuperUser()

        response = ThreadAdmin(Thread, admin.site).delete_view(request, thread_data['id'])
        template_names = set([
            'admin/delete_confirmation.html',
            'admin/disqus_backstore/delete_confirmation.html',
            'admin/disqus_backstore/thread/delete_confirmation.html',
        ])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.template_name), template_names)
        # dirty hack for formatting deleted_object context... Use the same formatting
        # in django.contrib.admin.utils.get_deleted_objects
        # the related post objects will be a list of post object,
        # so we have to put it into a list...
        deleted_objects = [format_html('{}: <a href="{}">{}</a>',
                                       capfirst(obj.__class__._meta.verbose_name),
                                       reverse('%s:%s_%s_change'%(
                                           admin.site.name,
                                           obj._meta.app_label,
                                           obj._meta.model_name
                                       ), None, (quote(obj._get_pk_val()),)),
                                       obj) for obj in [thread_object, related_post_object]]
        deleted_objects[1] = [deleted_objects[1]]
        self.assertEqual(sorted(response.context_data['deleted_objects']),
                         sorted(deleted_objects))

    @mock.patch.object(DisqusQuery, 'delete_thread')
    @mock.patch.object(DisqusQuery, 'delete_posts')
    @mock.patch.object(DisqusQuery, 'get_threads_list', return_value=THREADS_LIST_RESPONSE)
    @mock.patch.object(DisqusQuery, 'get_posts_list', return_value=POSTS_LIST_RESPONSE)
    def test_thread_delete_view__post__success(self, _, __, delete_posts_mock, delete_thread_mock):
        thread_data = THREADS_LIST_RESPONSE['response'][0]
        post_data = POSTS_LIST_RESPONSE['response'][0]
        thread_object = thread_factory(thread_data)
        related_post_object = post_factory(post_data)
        related_post_object.thread = thread_object
        # The way to create user is as same as the way in
        # `django.tests.admin_view.tests.AdminViewPermissionTests.test_delete_view`
        # Because RequestFactory can't handle MiddleWare,
        # even we set the `request._dont_enforce_csrf_checks to prevent csrf token check
        # We still need to handle the message for MessageMiddleWare used in admin view.
        # Workaround for this will make test code hard to understand.
        # So here I choose test it directly with `self.client`
        deleteuser = User.objects.create_user(
            username='deleteuser',
            password='secret',
            is_staff=True
        )
        deleteuser.user_permissions.add(
            get_perm(
                Thread,
                get_permission_codename('delete', Thread._meta)
            )
        )
        deleteuser.user_permissions.add(
            get_perm(
                Post,
                get_permission_codename('delete', Post._meta)
            )
        )
        self.client.force_login(deleteuser)
        delete_url, delete_dict = '/admin/disqus_backstore/thread/{id}/delete/'.format(id=thread_object.id), {'post':'yes'}

        response = self.client.post(delete_url, delete_dict)

        self.assertEqual(response.status_code, 302)
        delete_thread_mock.assert_called_once_with(thread_object.id)
        delete_posts_mock.assert_called_once()


class DisqusThreadQuerySetTest(TestCase):

    def test_get__normal_case__get_object_successfully(self):
        thread_data = THREADS_LIST_RESPONSE['response'][0]
        thread_id = int(thread_data.get('id'))
        with mock.patch.object(DisqusQuery, 'get_threads_list', return_value={
                'response': [thread_data,]
        }):
            obj = Thread.objects.get(id=thread_id)
            self.assertEqual(obj.id, thread_id)

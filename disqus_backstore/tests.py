from django.test import TestCase

class DisqusThreadsAdminTest(TestCase):

    def test_thread_model_in_change_list_view(self):
        response = self.client.get('/admin/disqus_back_store/threads/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_post_model_in_change_list_view(self):
        response = self.client.get('/admin/disqus_back_store/posts/', follow=True)
        self.assertEqual(response.status_code, 200)

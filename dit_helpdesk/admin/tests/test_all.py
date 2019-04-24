from django.test import TestCase, Client

from django.contrib.auth import get_user_model


class AdminSSOLoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create(
            email='test@test.com',
            is_staff=False,
            is_superuser=False
        )

    def test_login_authenticated_but_not_staff_leads_to_403(self):
        self.client.force_login(self.user)
        response = self.client.get('/admin/login/')

        self.assertEqual(response.status_code, 403)

    def test_login_authenticated_without_next_url_redirects_to_admin(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)

        response = self.client.get('/admin/login/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/')

    def test_login_authenticated_redirects_to_next_url(self):
        self.user.is_staff = True
        self.user.save()
        session = self.client.session
        session['admin_next_url'] = '/whatever/'
        session.save()
        self.client.force_login(self.user)

        response = self.client.get('/admin/login/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/whatever/')

    def test_login_redirects_to_sso_login(self):
        response = self.client.get('/admin/login/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/auth/login/')

    def test_login_saves_next_query_string_in_session(self):

        self.client.get('/admin/login/?next=/whatever/')

        self.assertEqual(self.client.session['admin_next_url'], '/whatever/')

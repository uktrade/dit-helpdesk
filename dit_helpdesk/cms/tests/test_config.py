from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.helpers import reset_urls_for_settings


User = get_user_model()


class TestConfig(TestCase):

    def setUp(self):
        with reset_urls_for_settings(CMS_ENABLED=True):
            self.url = reverse("cms:home")

    def test_hide_cms_logged_out_user(self):
        with reset_urls_for_settings(CMS_ENABLED=True):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 302)

        with reset_urls_for_settings(CMS_ENABLED=False):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 404)

    def test_hide_cms_logged_in_user(self):
        username = "testuser"
        email = "test@example.com"
        password = "test"
        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()
        self.client.login(username=user.username, password=password)

        with reset_urls_for_settings(CMS_ENABLED=True):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)

        with reset_urls_for_settings(CMS_ENABLED=False):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 404)

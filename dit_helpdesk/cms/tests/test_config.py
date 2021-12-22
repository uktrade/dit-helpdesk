from django.contrib.auth import get_user_model
from django.urls import reverse

from core.testutils import reset_urls_for_settings

from .base import CMSTestCase


User = get_user_model()


class TestConfig(CMSTestCase):
    def setUp(self):
        with reset_urls_for_settings(CMS_ENABLED=True):
            self.url = reverse("cms:regulation-groups-list")

    def test_hide_cms_logged_out_user(self):
        with reset_urls_for_settings(CMS_ENABLED=True):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 302)

        with reset_urls_for_settings(CMS_ENABLED=False):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 404)

    def test_hide_cms_logged_in_user(self):
        self.login()

        with reset_urls_for_settings(CMS_ENABLED=True):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)

        with reset_urls_for_settings(CMS_ENABLED=False):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 404)

from django.test import TestCase
from django.urls import reverse


class IndexViewTestCase(TestCase):
    """
    Test Index View
    """

    def test_index__returns_http_200(self):
        resp = self.client.get(reverse("index"))
        self.assertTrue(resp.status_code, 200)

from django.test import RequestFactory
from django.test import TestCase

from core.views import error500handler


class CoreViewsTestCase(TestCase):

    """
    Test Error pages
    """

    def test_404_error(self):
        resp = self.client.get("/non_existant_path/")
        self.assertEqual(resp.status_code, 404)

    def test_500_error(self):
        req = RequestFactory().get("/")
        resp = error500handler(req)
        self.assertEqual(resp.status_code, 500)

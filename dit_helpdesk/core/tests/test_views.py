from django.conf.urls import handler500
from django.http import HttpResponseServerError
from django.test import TestCase
from django.urls import reverse
from django.views.defaults import server_error
from django.test import RequestFactory

from core.views import error500handler


class CoreViewsTestCase(TestCase):

    """
    Test Error pages
    """

    def test_404_error(self):
        resp = self.client.get('/non_existant_path/')
        print(resp)
        self.assertEqual(resp.status_code, 404)

    def test_500_error(self):
        req = RequestFactory().get('/')
        resp = error500handler(req)
        self.assertEqual(resp.status_code, 500)
        self.assertTemplateUsed('core/500.html')

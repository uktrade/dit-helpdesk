from django.test import TestCase, Client, RequestFactory, override_settings
from django.http import HttpResponse
from django.conf import settings

from core.middleware import NoIndexMiddleware


class NoIndexMiddlewareTestCase(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.client = Client()

    def test_get_noindex_header_response(self):
        request = self.rf.get("/any_old_page/")

        middleware = NoIndexMiddleware(lambda _: HttpResponse(status=200))

        response = middleware(request)

        self.assertEqual("noindex, nofollow", response["X-Robots-Tag"])

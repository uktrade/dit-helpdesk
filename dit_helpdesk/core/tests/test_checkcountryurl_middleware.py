import logging
import random
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.conf import settings
from core.middleware import CheckCountryUrlMiddleware


class CheckCountryUrlMiddlewareTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.eu_country_codes = settings.EU_COUNTRY_CODES

    def test_url_with_country_code_of_eu_member_triggers_a_redirect(self):
        country_code = random.choice(self.eu_country_codes)
        request = self.factory.get(
            "/country/{0}/commodity/0202203011/104334".format(country_code.lower())
        )
        request.session = {}
        middleware = CheckCountryUrlMiddleware(lambda _: HttpResponse(status=200))
        response = middleware(request)
        self.assertEqual(response.status_code, 302)

    def test_url_with_country_code_of_eu_member_updates_country_session_variable_to_eu(
        self
    ):
        country_code = random.choice(self.eu_country_codes)
        request = self.factory.get(
            "/country/{0}/commodity/0202203011/104334".format(country_code.lower())
        )
        request.session = {}
        middleware = CheckCountryUrlMiddleware(lambda _: HttpResponse(status=200))
        middleware(request)
        self.assertEqual(request.session["origin_country"], "EU")

    def test_url_with_country_code_of_eu_member_redirects_to_eu_url(self):
        country_code = random.choice(self.eu_country_codes)
        request = self.factory.get(
            "/country/{0}/commodity/0202203011/104334".format(country_code.lower())
        )
        request.session = {}
        middleware = CheckCountryUrlMiddleware(lambda _: HttpResponse(status=200))
        response = middleware(request)
        self.assertEqual(response.url, "/country/eu/commodity/0202203011/104334")

    def test_url_with_country_code_of_eu_does_not_trigger_redirect(self):
        request = self.factory.get("/country/eu/commodity/0202203011/104334")
        request.session = {}
        middleware = CheckCountryUrlMiddleware(lambda _: HttpResponse(status=200))
        response = middleware(request)
        self.assertEqual(response.status_code, 200)

    def test_url_with_country_code_of_non_eu_does_not_trigger_redirect(self):
        request = self.factory.get("/country/ca/commodity/0202203011/104334")
        request.session = {}
        middleware = CheckCountryUrlMiddleware(lambda _: HttpResponse(status=200))
        response = middleware(request)
        self.assertEqual(response.status_code, 200)

from django.test import TestCase, Client, RequestFactory, override_settings
from django.http import HttpResponse
from django.conf import settings

from .ip_filter import get_client_ip
from .middleware import AdminIpRestrictionMiddleware


class AdminIPMiddlewareTestCase(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.client = Client()

    def test_get_client_ip_no_header(self):
        request = self.rf.get('/whatever/')

        client_ip = get_client_ip(request)

        self.assertIsNone(client_ip)

    @override_settings(IP_SAFELIST_XFF_INDEX=-3)
    def test_get_client_ip(self):
        request = self.rf.get('/whatever/', HTTP_X_FORWARDED_FOR='1.1.1.1, 2.2.2.2, 3.3.3.3')
        client_ip = get_client_ip(request)

        self.assertEqual(client_ip, '1.1.1.1')

    @override_settings(RESTRICT_ADMIN=True)
    def test_ip_restriction_middleware_is_enabled(self):

        self.assertEqual(self.client.get('/admin/').status_code, 401)

    @override_settings(RESTRICT_ADMIN=True)
    def test_ip_restriction_applies_to_admin_only(self):

        request = self.rf.get('/choose-country/')

        self.assertEqual(
            AdminIpRestrictionMiddleware(lambda _: HttpResponse(status=200))(request).status_code, 200)

    @override_settings(RESTRICT_ADMIN=False)
    def test_ip_restriction_enabled_false(self):

        request = self.rf.get('/admin/', HTTP_X_FORWARDED_FOR='')

        self.assertEqual(
            AdminIpRestrictionMiddleware(lambda _: HttpResponse(status=200))(request).status_code, 200)

    @override_settings(RESTRICT_ADMIN=True)
    def test_ip_restriction_missing_x_forwarded_header(self):

        request = self.rf.get('/admin/', HTTP_X_FORWARDED_FOR='1.1.1.1')

        self.assertEqual(
            AdminIpRestrictionMiddleware(lambda _: HttpResponse(status=200))(request).status_code, 401)

    @override_settings(RESTRICT_ADMIN=True)
    def test_ip_restriction_invalid_x_forwarded_header(self):

        request = self.rf.get('/admin/', HTTP_X_FORWARDED_FOR='1.1.1.1')

        self.assertEqual(
            AdminIpRestrictionMiddleware(lambda _: HttpResponse(status=200))(request).status_code, 401)

    @override_settings(RESTRICT_ADMIN=True, ALLOWED_ADMIN_IPS=['1.1.1.1'], IP_SAFELIST_XFF_INDEX=-3)
    def test_ip_restriction_valid_ip(self):

        request = self.rf.get('/admin/', HTTP_X_FORWARDED_FOR='1.1.1.1, 2.2.2.2, 3.3.3.3')

        self.assertEqual(
            AdminIpRestrictionMiddleware(lambda _: HttpResponse(status=200))(request).status_code, 200)

    @override_settings(RESTRICT_ADMIN=True, ALLOWED_ADMIN_IPS=['2.2.2.2'], IP_SAFELIST_XFF_INDEX=-3)
    def test_ip_restriction_invalid_ip(self):

        request = self.rf.get('/admin/', HTTP_X_FORWARDED_FOR='1.1.1.1, 2.2.2.2, 3.3.3.3')

        self.assertEqual(
            AdminIpRestrictionMiddleware(lambda _: HttpResponse(status=200))(request).status_code, 401)

        settings.ALLOWED_ADMIN_IPS = ['3.3.3.3']

        self.assertEqual(
            AdminIpRestrictionMiddleware(lambda _: HttpResponse(status=200))(request).status_code, 401)

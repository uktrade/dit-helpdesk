from django import http
from django.test import TestCase, Client
from django.test.client import RequestFactory

from core.views import error500handler


class CoreViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def test_handling_error_404(self):
        response = self.client.get('/this_is_not_the_web_page_you_were_looking_for.html')
        self.assertEqual(response.status_code, 404)

    def test_hanlding_error_500(self):
        factory = RequestFactory()
        request = factory.get('/')
        response = error500handler(request)
        self.assertEqual(response.status_code, 500)

    def test_hanlding_error_404_with_correct_template(self):
        response = self.client.get('/im_sorry_dave_Im_afraid_cant_do_that.html')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_hanlding_error_500_with_correct_template(self):
        factory = RequestFactory()
        request = factory.get('/')
        response = error500handler(request)
        self.assertInHTML(
            "Sorry, there is a problem with the service",
            response.content.decode('utf-8')
        )

from django.test import TestCase
from django.urls import reverse


class SearchViewTestCase(TestCase):

    """
    Test Search view
    """

    def setUp(self):
        pass

    fixtures = ['../../countries/fixtures/countries_data.json']

    def test_search_view_returns_http_200(self):
        resp = self.client.get(reverse('search', kwargs={"country_code": "AU"}))
        self.assertEqual(resp.status_code, 200)

    # def test_search_view_with_nonexisting_country_code_returns_http_302(self):
    #     resp = self.client.get(reverse('search', kwargs={"country_code": "XY"}))
    #     self.assertEqual(resp.status_code, 302)

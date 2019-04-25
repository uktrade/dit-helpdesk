from django.test import TestCase

from countries.models import Country


class CountryModelTestCase(TestCase):

    def setUp(self):
        self.country = Country.objects.create(country_code="UK", name="United Kingdom")

    def test_country_model_str(self):

        self.assertEquals(str(self.country), "UK United Kingdom")

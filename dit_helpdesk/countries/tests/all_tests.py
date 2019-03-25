from unittest import TestCase
from django.test import TransactionTestCase

from countries.models import Country


class CountryModelTransactionTestCase(TransactionTestCase):

    fixtures = ['countries/fixtures/countries_data.json']

    def test_fixtures_load_countries_data(self):
        self.assertTrue(Country.objects.count() > 0)
from django.test import TestCase
from django.apps import apps
from countries.apps import CountriesConfig


class CountriesConfigTestCase(TestCase):

    """
    Config tests
    """

    def test_config_name_is_countries(self):
        self.assertEqual(CountriesConfig.name, 'countries')

    def test_app_name_is_countries(self):
        self.assertEqual(apps.get_app_config('countries').name, 'countries')

from django.test import TestCase
from django.apps import apps
from commodities.apps import CommoditiesConfig


class CommoditiesConfigTestCase(TestCase):

    def test_apps(self):
        self.assertEqual(CommoditiesConfig.name,'commodities')
        self.assertEqual(apps.get_app_config('commodities').name, 'commodities')
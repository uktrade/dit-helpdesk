from django.test import TestCase
from django.apps import apps
from regulations.apps import RegulationsConfig


class RegulationsConfigTestCase(TestCase):
    """
    Test app config
    """

    def test_apps(self):
        self.assertEqual(RegulationsConfig.name,'regulations')
        self.assertEqual(apps.get_app_config('regulations').name, 'regulations')
from django.test import TestCase
from django.apps import apps
from rules_of_origin.apps import RulesOfOriginConfig


class RulesOfOriginConfigTestCase(TestCase):
    """
    Test app config
    """

    def test_apps(self):
        self.assertEqual(RulesOfOriginConfig.name, 'rules_of_origin')
        self.assertEqual(apps.get_app_config('rules_of_origin').name, 'rules_of_origin')

from django.test import TestCase
from django.apps import apps
from hierarchy.apps import HierarchyConfig


class HierarchyConfigTestCase(TestCase):

    def test_apps(self):
        self.assertEqual(HierarchyConfig.name, 'hierarchy')
        self.assertEqual(apps.get_app_config('hierarchy').name, 'hierarchy')

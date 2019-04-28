from django.test import TestCase
from django.apps import apps
from search.apps import SearchConfig


class SearchConfigTestCase(TestCase):

    def test_apps(self):
        self.assertEqual(SearchConfig.name,'search')
        self.assertEqual(apps.get_app_config('search').name, 'search')
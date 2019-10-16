from django.test import TestCase
from django.apps import apps
from iee_contact.apps import IEEContactConfig


class IEEContactConfigTestCase(TestCase):

    """
    Test app config
    """

    def test_apps(self):
        self.assertEqual(IEEContactConfig.name, "iee_contact")
        self.assertEqual(apps.get_app_config("iee_contact").name, "iee_contact")

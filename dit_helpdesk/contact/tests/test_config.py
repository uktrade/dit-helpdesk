from django.test import TestCase
from django.apps import apps
from contact.apps import ContactConfig


class ContactConfigTestCase(TestCase):

    """
    Test app config
    """

    def test_apps(self):
        self.assertEqual(ContactConfig.name, "contact")
        self.assertEqual(apps.get_app_config("contact").name, "contact")

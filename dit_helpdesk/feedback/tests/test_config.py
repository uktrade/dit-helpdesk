from django.test import TestCase
from django.apps import apps
from feedback.apps import FeedbackConfig


class FeedbackConfigTestCase(TestCase):
    """
    Test app config
    """

    """
    Test app config
    """

    def test_apps(self):
        self.assertEqual(FeedbackConfig.name, 'feedback')
        self.assertEqual(apps.get_app_config('feedback').name, 'feedback')

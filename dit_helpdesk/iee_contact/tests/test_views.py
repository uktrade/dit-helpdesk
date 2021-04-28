import logging

from django.test import TestCase, Client

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class IEEContactFormViewTestCase(TestCase):
    """
    Test Feedback View
    """

    def setUp(self):

        self.client = Client()
        self.wizard_url = "/iee_contact/"

    def test_initial_form_call(self):
        response = self.client.get(self.wizard_url)
        wizard = response.context["wizard"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(wizard["steps"].current, "step_one")
        self.assertEqual(wizard["steps"].step0, 0)
        self.assertEqual(wizard["steps"].step1, 1)
        self.assertEqual(wizard["steps"].last, "step_three")
        self.assertEqual(wizard["steps"].prev, None)
        self.assertEqual(wizard["steps"].next, "step_two")
        self.assertEqual(wizard["steps"].count, 3)

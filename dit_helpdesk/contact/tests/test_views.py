import logging

from django.test import TestCase, Client

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class ContactFormViewTestCase(TestCase):
    """
    Test Feedback View
    """

    def setUp(self):

        self.client = Client()
        self.wizard_url = "/contact/"

    def test_initial_form_call(self):

        session = self.client.session
        session["origin_country"] = "eu"
        session.save()

        response = self.client.get(self.wizard_url, follow=True)
        self.assertEqual(response.status_code, 200)
        wizard = response.context["wizard"]

        self.assertEqual(wizard["steps"].current, "step_one")
        self.assertEqual(wizard["steps"].step0, 0)
        self.assertEqual(wizard["steps"].step1, 1)
        self.assertEqual(wizard["steps"].last, "step_three")
        self.assertEqual(wizard["steps"].prev, None)
        self.assertEqual(wizard["steps"].count, 2)

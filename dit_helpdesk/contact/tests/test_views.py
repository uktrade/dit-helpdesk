import logging

from django.test import TestCase, Client
from django.urls import reverse

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

        contact_form_step_one = {
            "step_two-category": "1",
            "session_contact_wizard-current_step": "step_two",
        }
        contact_form_step_two = {
            "step_four-topic": "2",
            "session_contact_wizard-current_step": "step_three",
        }
        contact_form_step_three = {
            "step_four-name": "John Doe",
            "step_four-email_address": "john.doe@domain.com",
            "step_four-message": "The test message for the form",
            "step_four-terms_and_conditions": "True",
            "session_contact_wizard-current_step": "step_four",
        }
        wizard_steps_data = (
            contact_form_step_one,
            contact_form_step_two,
            contact_form_step_three,
        )

        response = self.client.get(self.wizard_url)
        wizard = response.context["wizard"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(wizard["steps"].current, "step_one")
        self.assertEqual(wizard["steps"].step0, 0)
        self.assertEqual(wizard["steps"].step1, 1)
        self.assertEqual(wizard["steps"].last, "step_three")
        self.assertEqual(wizard["steps"].prev, None)
        self.assertEqual(wizard["steps"].count, 2)

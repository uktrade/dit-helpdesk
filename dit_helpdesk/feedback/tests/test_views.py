import logging

from django.test import TestCase, Client
from django.urls import reverse

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class FeedbackViewTestCase(TestCase):
    """
    Test Feedback View
    """

    def setUp(self):

        self.client = Client()
        self.wizard_url = "/contact/"

    def test_get_feedback_view_with_no_country_code(self):
        resp = self.client.get(reverse("feedback-view"), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertTemplateUsed(resp, "countries/choose_country.html")

    def test_get_feedback_view_with_country_code(self):

        session = self.client.session
        session["origin_country"] = "eu"
        session.save()

        resp = self.client.get(reverse("feedback-view"), follow=True)
        self.assertEquals(resp.status_code, 200)
        self.assertTemplateUsed(resp, "contact/step_three.html")

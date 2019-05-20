import logging

from django.test import TestCase
from django.urls import reverse

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class FeedbackFormTestCase(TestCase):
    """
    Test Form
    """

    def test_submit_empty_message_form_returns_required_fields(self):
        resp = self.client.post(reverse('feedback-view'), {'name': 'test', 'email': 'test@test.com'})
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.resolver_match.url_name, 'feedback-view')

        form = resp.context['form']
        self.assertFalse(form.is_valid())
        logger.debug(form.errors)
        self.assertEquals(form.errors, {'message': ['Enter a message']},)

    def test_message_field_limit(self):
        message = 'This is a test message' * 50
        resp = self.client.post(
            reverse('feedback-view'),
            {'name': 'test', 'email': 'test@test.com', 'message': message},
        )

        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.resolver_match.url_name, 'feedback-view')
        form = resp.context['form']

        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors,
            {'message': ['Message needs to be less than 1,000 characters']},
        )

    def test_invalid_email_address(self):
        message = 'This is a test message'
        resp = self.client.post(
            reverse('feedback-view'),
            {'name': 'test', 'email': 'test', 'message': message},
        )
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.resolver_match.url_name, 'feedback-view')

        form = resp.context['form']
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors,
            {'email': ['Enter an email address in the correct format, like name@example.com',
                       'Enter an email address']},
        )

    def test_form_with_missing_name(self):
        message = 'This is a test message'
        resp = self.client.post(reverse('feedback-view'), {'message': message, 'email': 'test@test.com'})
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.resolver_match.url_name, 'feedback-view')

        form = resp.context['form']
        self.assertFalse(form.is_valid())
        logger.debug(form.errors)
        self.assertEquals(form.errors, {'name': ['Enter your full name']}, )

from django.test import TestCase
from django.urls import reverse


class FeedbackViewTestCase(TestCase):

    def test_get_feedback_view(self):
        resp = self.client.get(reverse('feedback-view'))
        self.assertEquals(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'feedback_form.html')

    def test_submitting_form_redirects_to_success_page(self):
        resp = self.client.post(
            reverse('feedback-view'),
            {'name': 'test', 'email': 'test@test.com', 'message': 'feedback'},
        )
        self.assertRedirects(resp, reverse('feedback-success-view'))

class FeedbackSuccessViewTestCase(TestCase):

    def test_get_success_view(self):
        resp = self.client.get(reverse('feedback-success-view'))
        self.assertEquals(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'feedback_success.html')
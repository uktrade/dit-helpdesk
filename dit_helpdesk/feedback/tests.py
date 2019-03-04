from django.test import TestCase
from django.urls import reverse


class TestFeedbackForm(TestCase):

    def test_get_feedback_view(self):
        response = self.client.get(reverse('feedback-view'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'feedback_form.html')

    def test_submit_empty_form_returns_required_fields(self):
        response = self.client.post(reverse('feedback-view'), {})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.resolver_match.url_name, 'feedback-view')
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors,
            {
                'name': ['This field is required.'],
                'email': ['This field is required.'],
                'message': ['This field is required.'],
            },
        )

    def test_submitting_form_redirects_to_success_page(self):
        response = self.client.post(
            reverse('feedback-view'),
            {'name': 'test', 'email': 'test@test.com', 'message': 'feedback'},
        )
        self.assertRedirects(response, reverse('feedback-success-view'))

    def test_message_field_limit(self):
        message = 'This is a test message' * 50
        response = self.client.post(
            reverse('feedback-view'),
            {'name': 'test', 'email': 'test@test.com', 'message': message},
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.resolver_match.url_name, 'feedback-view')
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors,
            {'message': ['Ensure this value has at most 1000 characters (it has 1100).']},
        )

    def test_invalid_email_address(self):
        message = 'This is a test message'
        response = self.client.post(
            reverse('feedback-view'),
            {'name': 'test', 'email': 'test', 'message': message},
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.resolver_match.url_name, 'feedback-view')
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.errors,
            {'email': ['Enter a valid email address.']},
        )


class TestFeedbackSuccessView(TestCase):

    def test_get_success_view(self):
        response = self.client.get(reverse('feedback-success-view'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'feedback_success.html')

from django import forms
from feedback.models import Feedback


class FeedbackForm(forms.ModelForm):

    class Meta:
        model = Feedback
        fields = ['message', 'name', 'email']
        error_messages = {
            'message': {
                'required': 'Enter a message',
                'max_length': 'Message needs to be less than 1,000 characters'
            },
            'name': {
                'max_length': 'Name entered needs to be less than 255 characters'
            },
            'email': {
                'invalid' : 'Enter an email address in the correct format, like name@example.com'
            }
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        name = cleaned_data.get("name")

        if name and not email:
            raise forms.ValidationError(
                {'email': ["Enter an email address"]}
            )

        if email and not name:
            raise forms.ValidationError(
                {'name': ["Enter your full name"]}
            )
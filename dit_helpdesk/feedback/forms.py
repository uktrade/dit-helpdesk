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
                'invalid' : 'Enter a valid email address'
            }
        }

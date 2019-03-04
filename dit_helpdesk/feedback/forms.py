from django import forms
from feedback.models import Feedback


class FeedbackForm(forms.ModelForm):

    class Meta:
        model = Feedback
        fields = ['message', 'name', 'email']
        error_messages = {
            'message': {
                'required': "Enter a message",
                'limit': "The message needs to be less than 1000 characters"
            },
            'email': {
                'invalid' : 'Enter a valid email address'
            }
        }

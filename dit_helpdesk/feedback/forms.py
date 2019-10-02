from django import forms
from feedback.models import Feedback


class FeedbackForm(forms.ModelForm):
    """
    ModelForm for feedback model with error message definitions
    """

    class Meta:
        model = Feedback
        fields = ["message", "name", "email"]
        error_messages = {
            "message": {
                "required": "Enter a message",
                "max_length": "Message needs to be less than 1,000 characters",
            },
            "name": {
                "required": "Enter your full name",
                "max_length": "Name entered needs to be less than 255 characters",
            },
            "email": {
                "required": "Enter an email address",
                "invalid": "Enter an email address in the correct format, like name@example.com",
            },
        }

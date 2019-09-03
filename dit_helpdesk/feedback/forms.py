from django import forms
from feedback.models import Feedback
from directory_forms_api_client.forms import ZendeskAPIForm

class FeedbackForm(forms.ModelForm):
    """
    ModelForm for feedback model with error message definitions
    """

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
                'invalid': 'Enter an email address in the correct format, like name@example.com'
            }
        }

    def clean(self):
        """
        form data cleansing and validation raises validation errors on failure
        :return: form object
        """
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


LOCATION_CHOICES = (
    (1, 'The UK'),
    (2, 'Outside the UK')
)

CATEGORY_CHOICES = (
    (1, 'Investing in the UK'),
    (2, 'Exporting to the UK'),
    (3, 'Find a UK business partner'),
    (4, 'EU exit enquiries'),
    (5, 'Other')
)

TOPIC_CHOICES = (
    (1, 'Commodity codes, tariffs and measures, import procedures'),
    (2, 'Importing animals, plants or food, environmental regulations, sanitary and phytosanitary regulations'),
    (3, 'Product safety and standards, packaging and labelling'),
    (4, 'Import controls, trade agreements, rules of origin'),
    (5, 'Exporting from a developing nation'),
    (6, 'Help using the "Trade with the UK: look up tariffs, taxes and rules" service'),
    (7, 'Other'),
)


class FeedbackFormStepOne(forms.Form):
    location = forms.ChoiceField(choices=LOCATION_CHOICES, widget=forms.RadioSelect)
    location.label = "Where are you based?"


class FeedbackFormStepTwo(forms.Form):
    enquiry_type = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.RadioSelect)


class FeedbackFormStepThree(forms.Form):
    pass


class FeedbackFormStepFour(forms.Form):
    enquiry_topic = forms.ChoiceField(choices=TOPIC_CHOICES, widget=forms.RadioSelect)


class FeedbackFormStepFive(forms.Form):
    name = forms.CharField()
    email_address = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    terms_and_conditions = forms.BooleanField()

    message.label="Tell us how we can help"
    message.help_text="Do not include personal or financial information, like your National Insurance number or credit card details."

    class Meta:
        model = Feedback
        fields = ['message', 'name', 'email_address']
        error_messages = {
            'message': {
                'required': 'Enter a message',
                'max_length': 'Message needs to be less than 1,000 characters'
            },
            'name': {
                'max_length': 'Name entered needs to be less than 255 characters'
            },
            'email': {
                'invalid': 'Enter an email address in the correct format, like name@example.com'
            }
        }

    def clean(self):
        """
        form data cleansing and validation raises validation errors on failure
        :return: form object
        """
        cleaned_data = super().clean()
        email_address = cleaned_data.get("email_address")
        name = cleaned_data.get("name")

        if name and not email_address:
            raise forms.ValidationError(
                {'email_address': ["Enter an email address"]}
            )

        if email_address and not name:
            raise forms.ValidationError(
                {'name': ["Enter your full name"]}
            )


class ZendeskForm(ZendeskAPIForm):
    # note that the base form provides `requester_email` email field
    name = forms.CharField()
    email_address = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
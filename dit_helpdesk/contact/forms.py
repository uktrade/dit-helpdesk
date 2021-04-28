from directory_forms_api_client.forms import ZendeskAPIForm, EmailAPIForm
from django import forms
from django.forms import fields

CATEGORY_CHOICES = ((1, "Exporting to the UK"), (2, "Technical help"))

TOPIC_CHOICES = (
    (1, "Commodity codes, tariffs and measures, import procedures"),
    (
        2,
        "Importing animals, plants or food, environmental regulations, sanitary and phytosanitary regulations",
    ),
    (3, "Product safety and standards, packaging and labelling"),
    (4, "Import controls, trade agreements, rules of origin"),
    (5, "Other"),
)

TOPIC_CHOICE_HELP_TEXT = (
    "You will be redirected to Her Majesty's Revenue and Customs (HMRC) contact form",
    "Your enquiry will be sent to the Department for Environment, Food and Rural Affairs (Defra)",
    "Your enquiry will be sent to the department for Business, Energy and Industrial Strategy (BEIS)",
    "Your enquiry will be sent to the Department for International Trade (DIT)",
    "Your enquiry will be sent to the Department for International Trade (DIT)",
)


class ContactFormStepOne(forms.Form):
    country_code = forms.CharField(widget=forms.HiddenInput, required=True)
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES, widget=forms.RadioSelect, required=True
    )
    category.label = "What would you like to know more about?"


class ContactFormStepTwo(forms.Form):
    country_code = forms.CharField(widget=forms.HiddenInput, required=True)
    topic = forms.ChoiceField(
        choices=TOPIC_CHOICES, widget=forms.RadioSelect, required=True
    )
    topic.label = "What would you like to know more about?"
    topic.help_text = TOPIC_CHOICE_HELP_TEXT


class ContactFormStepThree(forms.Form):
    name = forms.CharField(required=True)
    email_address = forms.EmailField(required=True)
    terms_and_conditions = forms.BooleanField(required=True)
    country_code = forms.CharField(widget=forms.HiddenInput, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    message.label = "Tell us how we can help"
    message.help_text = "Do not include personal or financial information, like your National Insurance number or credit card details."  # noqa: E501

    class Meta:

        fields = ["message", "name", "email_address", "terms_and_conditions"]
        error_messages = {
            "message": {
                "required": "Enter a message",
                "max_length": "Message needs to be less than 1,000 characters",
            },
            "name": {
                "required": "Enter your fullname",
                "max_length": "Name entered needs to be less than 255 characters",
            },
            "email_address": {
                "required": "Enter your email address",
                "invalid": "Enter an email address in the correct format, like name@example.com",
            },
            "terms_and_conditions": {
                "required": "Enter your email address",
                "invalid": "Enter an email address in the correct format, like name@example.com",
            },
        }


class ZendeskForm(ZendeskAPIForm):
    # note that the base form provides `requester_email` email field
    name = forms.CharField()
    email_address = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)


class ZendeskEmailForm(EmailAPIForm):
    message = fields.CharField()

    @property
    def text_body(self):
        """Override text_body to text template of email body."""

        text = str(self.cleaned_data["message"])
        return text

    @property
    def html_body(self):
        """Override html_body to return html template of email body."""
        cleaned = str(self.cleaned_data["message"]).replace("\n", "<br />")
        cleaned_html = "<p>" + cleaned + "</p>"
        return cleaned_html

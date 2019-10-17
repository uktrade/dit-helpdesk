from directory_forms_api_client.forms import ZendeskAPIForm
from django import forms

IEE_LOCATION_CHOICES = ((1, "Exporting from the UK"), (2, "Brexit enquiries"))

IEE_TOPIC_CHOICES = (
    (
        1,
        "Customs declarations and procedures, commodity codes, duties and tariff rates",
    ),
    (
        2,
        "Exporting animals, plants or food, environmental regulations, sanitary & phytosanitary regulations",
    ),
    (3, "Exporting cultural goods"),
    (4, "Exporting any other products"),
    (6, "Technical help with using the 'Export goods from the UK' service itself"),
)


class IEEContactFormStepOne(forms.Form):
    location = forms.ChoiceField(
        choices=IEE_LOCATION_CHOICES, widget=forms.RadioSelect, required=True
    )
    location.label = "What would you like to know more about?"


class IEEContactFormStepTwo(forms.Form):
    enquiry_topic = forms.ChoiceField(
        choices=IEE_TOPIC_CHOICES, widget=forms.RadioSelect, required=True
    )
    enquiry_topic.label = "What would you like to know more about?"


class IEEContactFormStepThree(forms.Form):
    name = forms.CharField(required=True)
    email_address = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    terms_and_conditions = forms.BooleanField(required=True)

    message.label = "Tell us how we can help"
    message.help_text = "Do not include personal or financial information, like your National Insurance number or credit card details."

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


class IEEZendeskForm(ZendeskAPIForm):
    # note that the base form provides `requester_email` email field
    name = forms.CharField()
    email_address = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

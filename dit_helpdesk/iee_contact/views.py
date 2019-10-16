import logging

from directory_forms_api_client import helpers
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import get_template
from formtools.wizard.views import SessionWizardView

from iee_contact.forms import (
    IEEContactFormStepOne,
    IEEContactFormStepTwo,
    IEEContactFormStepThree,
    IEE_LOCATION_CHOICES,
    IEE_TOPIC_CHOICES,
    IEEZendeskForm,
)

logger = logging.getLogger(__name__)


FORMS = [
    ("step_one", IEEContactFormStepOne),
    ("step_two", IEEContactFormStepTwo),
    ("step_three", IEEContactFormStepThree),
]

TEMPLATES = {
    "step_one": "iee_contact/step_one.html",
    "step_two": "iee_contact/step_two.html",
    "step_three": "iee_contact/step_three.html",
}

LOCATIONS, TOPICS = (dict(IEE_LOCATION_CHOICES), dict(IEE_TOPIC_CHOICES))


class IEEContactFormWizardView(SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    form_list = FORMS

    def done(self, form_list, **kwargs):
        context = self.process_form_data(form_list)

        # if the chosen topic is in the last four options then go to zendesk
        # otherwise send an email

        print(
            "settings.DIRECTORY_FORMS_API_BASE_URL: ",
            settings.DIRECTORY_FORMS_API_BASE_URL,
        )
        if context["topic"] in list(TOPICS.values())[4:]:
            IEEContactFormWizardView.send_to_zenddesk(context)
        else:
            IEEContactFormWizardView.send_mail(context)

        return render_to_response("iee_contact/done.html", {"context": context})

    def render_next_step(self, form, **kwargs):
        """
        override next steps for step five if enquiry_topic is
        Commodity codes, tariffs and measures, import procedures
        :param form: submitted form
        :param kwargs: passed keyword arguments
        :return: render to response
        """
        if (
            self.steps.next == "step_three"
            and form.cleaned_data["enquiry_topic"] == "1"
        ):
            return HttpResponseRedirect(settings.HMRC_TAX_FORM_URL)
        else:
            return super(IEEContactFormWizardView, self).render_next_step(
                form, **kwargs
            )

    @staticmethod
    def process_form_data(form_list):
        form_data = [form.cleaned_data for form in form_list]

        context = {"subject": "New IEE Enquiry", "service_name": "UK IEE"}

        for form in form_data:
            if "location" in form.keys():
                context["location"] = LOCATIONS[int(form["location"])]
            if "enquiry_topic" in form.keys():
                context["topic"] = TOPICS[int(form["enquiry_topic"])]
            if "email_address" in form.keys():
                context["email_address"] = form["email_address"]
            if "name" in form.keys():
                context["name"] = form["name"]
            if "message" in form.keys():
                context["message"] = form["message"]

        if context["topic"] == TOPICS[2]:
            context["recipient_email"] = "defra.helpline@defra.gov.uk"
            context["recipient_full_name"] = "DEFRA"

        elif context["topic"] == TOPICS[3]:
            context["recipient_email"] = "TBC"
            context["recipient_full_name"] = "TBC"

        elif context["topic"] == TOPICS[4]:
            context["recipient_email"] = "David.Hughes10@homeoffice.gov.uk"
            context["recipient_full_name"] = "David Hughes"

        elif context["topic"] == TOPICS[5]:
            context["destination"] = "zendesk euexit@trade.gov.uk"
            context["recipient_full_name"] = "Martin Cook"

        elif context["topic"] == TOPICS[6]:
            context["destination"] = "zendesk euexit@trade.gov.uk"
            context["recipient_full_name"] = "Martin Cook"

        elif context["topic"] == TOPICS[7]:
            context["destination"] = "zendesk euexit@trade.gov.uk"
            context["recipient_full_name"] = "ajid @ live services"

        elif context["topic"] == TOPICS[8]:
            context["destination"] = "zendesk euexit@trade.gov.uk"
            context["recipient_full_name"] = "Martin Cook"

        template = get_template("iee_contact/contact_message_tmpl.txt")
        context["content"] = template.render(context)

        return context

    @staticmethod
    def send_mail(context):

        headers = {"Reply-To": context["email_address"]}

        email = EmailMessage(
            context["subject"],
            context["content"],
            context["email_address"],
            [context["recipient_email"]],
            headers=headers,
        )

        try:
            email.send()
        except Exception as ex:
            print(ex.args)

    @staticmethod
    def send_to_zenddesk(context):

        zendesk_form = IEEZendeskForm(
            data={
                "message": context["message"],
                "email_address": context["email_address"],
                "name": context["name"],
            }
        )

        spam_control = helpers.SpamControl(contents=context["content"])

        sender = helpers.Sender(email_address=context["email_address"])

        assert zendesk_form.is_valid()

        if settings.DIRECTORY_FORMS_API_BASE_URL:

            zendesk_form.save(
                email_address=context["email_address"],
                full_name=context["name"],
                form_url="/iee_contact/",
                service_name=context["service_name"],
                spam_control=spam_control,
                sender=sender,
                subject=context["subject"],
            )

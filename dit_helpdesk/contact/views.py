import logging

from directory_forms_api_client import helpers
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import get_template
from formtools.wizard.views import SessionWizardView

from contact import constants
from contact.forms import (
    ContactFormStepOne,
    ContactFormStepTwo,
    ContactFormStepThree,
    ContactFormStepFour,
    LOCATION_CHOICES,
    CATEGORY_CHOICES,
    TOPIC_CHOICES,
    ZendeskForm,
    ZendeskEmailForm,
)

logger = logging.getLogger(__name__)


FORMS = [
    ("step_one", ContactFormStepOne),
    ("step_two", ContactFormStepTwo),
    ("step_three", ContactFormStepThree),
    ("step_four", ContactFormStepFour),
]

TEMPLATES = {
    "step_one": "contact/step_one.html",
    "step_two": "contact/step_two.html",
    "step_three": "contact/step_three.html",
    "step_four": "contact/step_four.html",
}

LOCATIONS, CATEGORIES, TOPICS = (
    dict(LOCATION_CHOICES),
    dict(CATEGORY_CHOICES),
    dict(TOPIC_CHOICES),
)


class ContactFormWizardView(SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    form_list = FORMS

    def done(self, form_list, **kwargs):
        context = self.process_form_data(form_list)

        if context["type"] == "Zendesk":
            resp = ContactFormWizardView.send_to_zenddesk(context)
        else:
            resp = ContactFormWizardView.send_mail(context)

        return render_to_response("contact/done.html", {"context": context})

    def render_next_step(self, form, **kwargs):
        """
        override next steps for step five if enquiry_topic is
        Commodity codes, tariffs and measures, import procedures
        :param form: submitted form
        :param kwargs: passed keyword arguments
        :return: render to response
        """
        print("Form: :", form)
        if (
            "enquiry_topic" in form.cleaned_data
            and self.steps.next == "step_three"
            and form.cleaned_data["enquiry_topic"] == "1"
        ):
            return HttpResponseRedirect(settings.HMRC_TAX_FORM_URL)
        else:
            return super(ContactFormWizardView, self).render_next_step(form, **kwargs)

    @staticmethod
    def process_form_data(form_list):
        form_data = [form.cleaned_data for form in form_list]

        context = {"subject": constants.SUBJECT, "service_name": constants.SERVICE_NAME}

        for form in form_data:
            if "location" in form.keys():
                context["location"] = LOCATIONS[int(form["location"])]
            if "enquiry_type" in form.keys():
                context["category"] = CATEGORIES[int(form["enquiry_type"])]
            if "enquiry_topic" in form.keys():
                context["topic"] = TOPICS[int(form["enquiry_topic"])]
            if "email_address" in form.keys():
                context["email_address"] = form["email_address"]
            if "name" in form.keys():
                context["name"] = form["name"]
            if "message" in form.keys():
                context["message"] = form["message"]

        if context["topic"] == TOPICS[2]:
            # Importing animals, plants or food, environmental regulations, sanitary and phytosanitary regulations
            context["type"] = "Email"
            context["recipient_email"] = settings.DEFRA_EMAIL
            context["recipient_full_name"] = settings.DEFRA_CONTACT

        elif context["topic"] == TOPICS[3]:
            # Product safety and standards, packaging and labelling
            context["type"] = "Email"
            context["recipient_email"] = settings.BEIS_EMAIL
            context["recipient_full_name"] = settings.BEIS_CONTACT

        elif context["topic"] == TOPICS[4]:
            # Topic: Import controls, trade agreements, rules of origin
            context["type"] = "Zendesk"
            context["subject"] += constants.DDAT_SUBJECT_SUFFIX
            context["subdomain"] = constants.DIT_SUBDOMAIN

        elif context["topic"] == TOPICS[5]:
            # TOPIC: Help using the “Trade with the UK: look up tariffs, taxes and rules” service
            context["type"] = "Zendesk"
            context["subject"] += constants.DIT_SUBJECT_SUFFIX
            context["subdomain"] = constants.DIT_SUBDOMAIN
            # go to  headed up by  (internal zendesk instance support@uktrade.zendesk.com same place as feedback we are using Forms API for)

        elif context["topic"] == TOPICS[6]:
            # Other
            context["type"] = "Zendesk"
            context["subject"] += " DIT EU Exit Enquiries"
            context["subdomain"] = constants.DIT_SUBDOMAIN

        template = get_template("contact/contact_message_tmpl.txt")

        context["content"] = template.render(context)

        context["spam_control"] = helpers.SpamControl(contents=context["content"])

        context["sender"] = helpers.Sender(email_address=context["email_address"])

        context["form_url"] = "/contact/"

        return context

    @staticmethod
    def send_mail(context):
        email_form = ZendeskEmailForm(data={"message": context["content"]})

        assert email_form.is_valid()

        resp = email_form.save(
            recipients=[context["recipient_email"], "glen.lavery@digital.trade.gov.uk"],
            subject=context["subject"],
            reply_to=[context["email_address"]],
            form_url=context["form_url"],
        )
        return resp

    @staticmethod
    def send_to_zenddesk(context):
        zendesk_form = ZendeskForm(
            data={
                "message": context["content"],
                "email_address": context["email_address"],
                "name": context["name"],
            }
        )
        assert zendesk_form.is_valid()
        resp = zendesk_form.save(
            email_address=context["email_address"],
            full_name=context["name"],
            form_url=context["form_url"],
            service_name=context["service_name"],
            spam_control=context["spam_control"],
            sender=context["sender"],
            subject=context["subject"],
            subdomain=context["subdomain"],
        )
        return resp

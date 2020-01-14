import logging

from directory_forms_api_client import helpers
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template.loader import get_template
from django.urls import reverse
from formtools.wizard.views import SessionWizardView

from contact import constants
from contact.forms import (
    ContactFormStepOne,
    ContactFormStepTwo,
    ContactFormStepThree,
    CATEGORY_CHOICES,
    TOPIC_CHOICES,
    ZendeskForm,
    ZendeskEmailForm,
    TOPIC_CHOICE_HELP_TEXT,
)
from core.views import error500handler
from countries.models import Country

logger = logging.getLogger(__name__)

FORMS = [
    ("step_one", ContactFormStepOne),
    ("step_two", ContactFormStepTwo),
    ("step_three", ContactFormStepThree),
]

TEMPLATES = {
    "step_one": "contact/step_one.html",
    "step_two": "contact/step_two.html",
    "step_three": "contact/step_three.html",
}

CATEGORIES, TOPICS = (dict(CATEGORY_CHOICES), dict(TOPIC_CHOICES))


def jump_to_step_two(wizard):
    """ Returning false bypasses the first form"""
    if wizard.request.path == "/feedback/":
        return False
    else:
        return True


def jump_to_step_three(wizard):
    """ Returning False bypasses second form """
    cleaned_data = wizard.get_cleaned_data_for_step("step_one") or {}
    category = cleaned_data.get("category")
    if not cleaned_data:
        category = "3"
    if category == "3":
        return False
    else:
        return True


class ContactFormWizardView(SessionWizardView):
    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    form_list = FORMS

    initial_dict = {"step_one": {"category": 1}, "step_two": {"topic": 1}}

    condition_dict = {"step_one": jump_to_step_two, "step_two": jump_to_step_three}

    def post(self, request, *args, **kwargs):

        if "origin_country" not in request.session:
            messages.error(
                request, "Please choose a country of origin before you proceed"
            )
            return redirect(reverse("choose-country"))

        return super(ContactFormWizardView, self).post(request, *args, **kwargs)

    def done(self, form_list, **kwargs):
        context = self.process_form_data(form_list)

        context["topic_help"] = TOPIC_CHOICE_HELP_TEXT

        if "origin_country" in self.request.session:
            context["country_code"] = self.request.session["origin_country"]

        if self.request.path == "/feedback/":
            context["subject"] = "Trade Helpdesk Feedback"
            context["recipient_email"] = settings.FEEDBACK_EMAIL
            context["recipient_fullname"] = settings.FEEDBACK_CONTACT
            template = get_template("contact/feedback_message_tmpl.txt")
            context["content"] = template.render(context)
            context["spam_control"] = helpers.SpamControl(contents=context["content"])
        else:
            context["subject"] = constants.SUBJECT

        if context["type"] == "Zendesk":
            try:
                ContactFormWizardView.send_to_zenddesk(context)
            except Exception as ex:
                logger.debug("Exception context: ", context)
                logger.info("Exception args:: ", ex.args)
                return error500handler(self.request)
        else:
            try:
                ContactFormWizardView.send_mail(context)
            except Exception as ex:
                logger.debug("Exception context: ", context)
                logger.info("Exception args: ", ex.args)
                return error500handler(self.request)

        return render_to_response("contact/done.html", {"context": context})

    def render_next_step(self, form, **kwargs):
        """
        override next steps for step five if enquiry_topic is
        Commodity codes, tariffs and measures, import procedures
        :param form: submitted form
        :param kwargs: passed keyword arguments
        :return: render to response
        """

        if (
            "topic" in form.cleaned_data
            and self.steps.next == "step_three"
            and form.cleaned_data["topic"] == "1"
        ):
            return HttpResponseRedirect(constants.HMRC_TAX_FORM_URL)
        else:
            return super(ContactFormWizardView, self).render_next_step(form, **kwargs)

    @staticmethod
    def process_form_data(form_list):
        form_data = [form.cleaned_data for form in form_list]

        context = {"service_name": constants.SERVICE_NAME, "subject": constants.SUBJECT}

        for form in form_data:

            if "country_code" in form.keys():
                context["country_code"] = form["country_code"]

            context["location"] = Country.objects.get(
                country_code=context["country_code"]
            ).name

            if "category" in form.keys():
                context["category"] = CATEGORIES[int(form["category"])]

            if "topic" in form.keys():
                context["topic"] = TOPICS[int(form["topic"])]

            if "email_address" in form.keys():
                context["email_address"] = form["email_address"]

            if "name" in form.keys():
                context["name"] = form["name"]

            if "message" in form.keys():
                context["message"] = form["message"]

            if "topic" in context.keys() and context["topic"] == TOPICS[2]:
                # Importing animals, plants or food, environmental regulations, sanitary and phytosanitary regulations
                context["type"] = "Email"
                context["recipient_email"] = settings.DEFRA_EMAIL
                context["recipient_fullname"] = settings.DEFRA_CONTACT

            elif "topic" in context.keys() and context["topic"] == TOPICS[3]:
                # Product safety and standards, packaging and labelling
                context["type"] = "Email"
                context["recipient_email"] = settings.BEIS_EMAIL
                context["recipient_fullname"] = settings.BEIS_CONTACT

            elif "topic" in context.keys() and context["topic"] == TOPICS[4]:
                # Topic: Import controls, trade agreements, rules of origin
                context["type"] = "Zendesk"
                context["subject"] += constants.DDAT_SUBJECT_SUFFIX
                context["subdomain"] = constants.DIT_SUBDOMAIN

            elif "topic" in context.keys() and context["topic"] == TOPICS[5]:
                # Other
                context["type"] = "Zendesk"
                context["subject"] += " DIT EU Exit Enquiries"
                context["subdomain"] = constants.DIT_SUBDOMAIN

                template = get_template("contact/contact_message_tmpl.txt")

                context["content"] = template.render(context)

        else:
            """ Copied from contact forms #TODO: fix others accordingly """
            context["type"] = "Zendesk"
            context["recipient_email"] = constants.FEEDBACK_EMAIL
            context["recipient_fullname"] = constants.FEEDBACK_FULLNAME
            context["subdomain"] = "dit"

            template = get_template("contact/feedback_message_tmpl.txt")
            context["content"] = template.render(context)

        context["spam_control"] = helpers.SpamControl(contents=context["content"])

        context["sender"] = helpers.Sender(
            country_code=context["country_code"], email_address=context["email_address"]
        )

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

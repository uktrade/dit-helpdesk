import logging

from directory_forms_api_client import helpers
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import get_template
from django.urls import reverse
from formtools.wizard.views import SessionWizardView

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

from countries.models import Country

logger = logging.getLogger(__name__)

FORMS = (
    ("step_one", ContactFormStepOne),
    ("step_two", ContactFormStepTwo),
    ("step_three", ContactFormStepThree),
)

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

    def dispatch(self, request, *args, **kwargs):

        if "origin_country" not in request.session:
            # messages.error(request, "Enter a country")
            return redirect(reverse("choose-country") + "?select-country")

        return super(ContactFormWizardView, self).dispatch(request, *args, **kwargs)

    def done(self, form_list, **kwargs):

        context = self.process_form_data(form_list, self.request.path)

        context["topic_help"] = TOPIC_CHOICE_HELP_TEXT

        if context["type"] == "Zendesk":
            resp = ContactFormWizardView.send_to_zendesk(context)
        else:
            resp = ContactFormWizardView.send_mail(context)

        logger.info("FORM Submittion response: {} ".format(resp))
        logger.info("FORM Submittion response json: {} ".format(resp.json()))

        data = [form.cleaned_data for form in form_list]

        logger.info("FORM Data: ", data)

        return render(self.request, "contact/done.html", {"form_data": data})

    def render_next_step(self, form, **kwargs):
        """
        override next steps for step five if enquiry_topic is
        Commodity codes, tariffs and measures, import procedures
        :param form: submitted form
        :param kwargs: passed keyword arguments
        :return: render to response
        """

        try:
            next_step = self.steps.next
        except ValueError:
            next_step = "step_three" if self.steps.current == "step_two" else None

        if (
            "topic" in form.cleaned_data
            and next_step == "step_three"
            and form.cleaned_data["topic"] == "1"
        ):
            return HttpResponseRedirect(settings.HMRC_TAX_FORM_URL)
        else:
            return super(ContactFormWizardView, self).render_next_step(form, **kwargs)

    def process_form_data(self, form_list, form_path):

        form_data = self.get_all_cleaned_data()

        is_feedback = (
            True if form_path == "/feedback/" or form_data["category"] == "3" else False
        )

        country_code = self.request.session["origin_country"]
        country_code = country_code.upper()

        context = {
            "country_code": country_code,
            "service_name": settings.SERVICE_NAME,
            "location": Country.objects.get(country_code=country_code).name,
            "email_address": form_data["email_address"],
            "name": form_data["name"],
            "message": form_data["message"],
            "form_url": form_path,
        }

        if is_feedback:
            context["type"] = "Zendesk"
            context["recipient_email"] = settings.FEEDBACK_EMAIL
            context["recipient_fullname"] = settings.FEEDBACK_CONTACT

        if is_feedback:
            if "category" not in form_data.keys():
                context["subject"] = settings.FEEDBACK_SUBJECT
            else:
                context["subject"] = settings.SUPPORT_SUBJECT
        else:
            context["subject"] = settings.CONTACT_SUBJECT

        if "category" in form_data.keys():
            context["category"] = CATEGORIES[int(form_data["category"])]

            if "topic" in form_data.keys():

                context["topic"] = TOPICS[int(form_data["topic"])]
                if form_data["topic"] == "2":
                    # Importing animals, plants or food, environmental regulations, sanitary and phytosanitary regulations
                    context["type"] = "Email"
                    context["recipient_email"] = settings.DEFRA_EMAIL
                    context["recipient_fullname"] = settings.DEFRA_CONTACT
                elif form_data["topic"] == "3":
                    # Product safety and standards, packaging and labelling
                    context["type"] = "Email"
                    context["recipient_email"] = settings.BEIS_EMAIL
                    context["recipient_fullname"] = settings.BEIS_CONTACT
                elif form_data["topic"] == "4":
                    # Topic: Import controls, trade agreements, rules of origin
                    context["type"] = "Zendesk"
                    context["subject"] += settings.DDAT_SUBJECT_SUFFIX
                    context["subdomain"] = settings.DIT_SUBDOMAIN
                    context["recipient_fullname"] = settings.DDAT_CONTACT
                elif form_data["topic"] == "5":
                    # Other
                    context["type"] = "Zendesk"
                    context["subject"] += settings.DIT_SUBJECT_SUFFIX
                    context["recipient_fullname"] = settings.DIT_CONTACT

        context["subdomain"] = (
            settings.DIT_SUBDOMAIN if context["type"] == "Zendesk" else ""
        )

        msg_tmpl = (
            "contact/feedback_message_tmpl.txt"
            if is_feedback
            else "contact/contact_message_tmpl.txt"
        )
        template = get_template(msg_tmpl)
        context["content"] = template.render(context)
        context["spam_control"] = helpers.SpamControl(contents=context["content"])
        context["sender"] = helpers.Sender(
            country_code=context["country_code"], email_address=context["email_address"]
        )

        return context

    @staticmethod
    def send_mail(context):
        email_form = ZendeskEmailForm(data={"message": context["content"]})

        assert email_form.is_valid()

        resp = email_form.save(
            recipients=[context["recipient_email"]],
            subject=context["subject"],
            reply_to=[context["email_address"]],
            form_url=context["form_url"],
        )
        return resp

    @staticmethod
    def send_to_zendesk(context):

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

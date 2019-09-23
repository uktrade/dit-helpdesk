import logging

from directory_forms_api_client import helpers
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.loader import get_template
from formtools.wizard.views import SessionWizardView

from contact.forms import ContactFormStepOne, ContactFormStepTwo, \
    ContactFormStepFour, ContactFormStepFive, LOCATION_CHOICES, CATEGORY_CHOICES, TOPIC_CHOICES, ZendeskForm

logger = logging.getLogger(__name__)


FORMS = [("step_one", ContactFormStepOne),
         ("step_two", ContactFormStepTwo),
         ("step_four", ContactFormStepFour),
         ("step_five", ContactFormStepFive)]

TEMPLATES = {"step_one": "contact/step_one.html",
             "step_two": "contact/step_two.html",
             "step_four": "contact/step_four.html",
             "step_five": "contact/step_five.html"}

LOCATIONS, CATEGORIES, TOPICS = (dict(LOCATION_CHOICES), dict(CATEGORY_CHOICES), dict(TOPIC_CHOICES))


class ContactFormWizardView(SessionWizardView):

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    form_list = FORMS

    def done(self, form_list, **kwargs):
        context = self.process_form_data(form_list)

        if context['topic'] in list(TOPICS.values())[4:]:
            ContactFormWizardView.send_to_zenddesk(context)
        else:
            ContactFormWizardView.send_mail(context)

        return render_to_response('contact/done.html', {'context': context})

    def render_next_step(self, form, **kwargs):
        """
        override next steps for step five if enquiry_topic is
        Commodity codes, tariffs and measures, import procedures
        :param form: submitted form
        :param kwargs: passed keyword arguments
        :return: render to response
        """
        if self.steps.next == 'step_five' and form.cleaned_data['enquiry_topic'] == '1':
            return HttpResponseRedirect('https://www.tax.service.gov.uk/shortforms/form/CITEX_CGEF')
        else:
            return super(ContactFormWizardView, self).render_next_step(form, **kwargs)

    @staticmethod
    def process_form_data(form_list):
        form_data = [form.cleaned_data for form in form_list]

        context = {
            'subject': "New UK Trade Helpdesk Enquiry",
            'service_name': "UK Trade Helpdesk"
        }

        for form in form_data:
            if 'location' in form.keys():
                context['location'] = LOCATIONS[int(form['location'])]
            if 'enquiry_type' in form.keys():
                context['category'] = CATEGORIES[int(form['enquiry_type'])]
            if 'enquiry_topic' in form.keys():
                context['topic'] = TOPICS[int(form['enquiry_topic'])]
            if 'email_address' in form.keys():
                context['email_address'] = form['email_address']
            if 'name' in form.keys():
                context['name'] = form['name']
            if 'message' in form.keys():
                context['message'] = form['message']

        if context['topic'] == TOPICS[2]:
            # Importing animals, plants or food, environmental regulations, sanitary and phytosanitary regulations
            context['recipient_email'] = "euexitDIT@defra.gov.uk"
            context['recipient_full_name'] = "DEFRA"

        elif context['topic'] == TOPICS[3]:
            # Product safety and standards, packaging and labelling
            context['recipient_email'] = "enquiries@beis.gov.uk"
            context['recipient_full_name'] = "BEIS"

        elif context['topic'] == TOPICS[4]:
            # Topic: Import controls, trade agreements, rules of origin
            context['destination'] = "Send to the DIT EU exit enquiries Zendesk - Susan Watersons Team"

        elif context['topic'] == TOPICS[5]:
            # TOPIC: Help using the “Trade with the UK: look up tariffs, taxes and rules” service
            context['destination'] = """go to DDAT support team headed up by Madeline Lasko (internal zendesk instance 
                            support@uktrade.zendesk.com same place as feedback we are using Forms API for)"""

        elif context['topic'] == TOPICS[6]:
            # Other
            destination = "Send to the DIT EU exit enquiries Zendesk - Susan Watersons Team"

        template = get_template('contact/contact_message_tmpl.txt')
        context['content'] = template.render(context)

        return context

    @staticmethod
    def send_mail(context):

        headers = {'Reply-To': context['email_address']}

        email = EmailMessage(
            context['subject'],
            context['content'],
            context['email_address'],
            [context['recipient_email']],
            headers=headers
        )

        email.send()

    @staticmethod
    def send_to_zenddesk(context):

        zendesk_form = ZendeskForm(data={
            'message': context['message'],
            'email_address': context['email_address'],
            'name': context['name']
        })

        spam_control = helpers.SpamControl(
            contents=context['content']
        )

        sender = helpers.Sender(
            email_address=context['email_address'],
        )

        assert zendesk_form.is_valid()

        if settings.DIRECTORY_FORMS_API_BASE_URL:

            zendesk_form.save(
                email_address=context['email_address'],
                full_name=context['name'],
                form_url='/contact/',
                service_name=context['service_name'],
                spam_control=spam_control,
                sender=sender,
                subject=context['subject']
            )


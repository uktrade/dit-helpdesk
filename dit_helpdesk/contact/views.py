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


class ContactFormWizardView(SessionWizardView):

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    form_list = FORMS

    def done(self, form_list, **kwargs):
        form_data = self.process_form_data(form_list)

        return render_to_response('contact/done.html', {'form_data': form_data})

    def render_next_step(self, form, **kwargs):
        """
        This method gets called when the next step/form should be rendered.
        `form` contains the last/current form.
        """
        # get the form instance based on the data from the storage backend
        # (if available).
        next_step = self.steps.next

        if next_step == 'step_five' and form.cleaned_data['enquiry_topic'] == '1':
            return HttpResponseRedirect('https://www.tax.service.gov.uk/shortforms/form/CITEX_CGEF')

        else:
            new_form = self.get_form(next_step,
                                     data=self.storage.get_step_data(next_step),
                                     files=self.storage.get_step_files(next_step))
            # change the stored current step
            self.storage.current_step = next_step
            return self.render(new_form, **kwargs)

    @staticmethod
    def process_form_data(form_list):
        form_data = [form.cleaned_data for form in form_list]

        locations, categories, topics = (dict(LOCATION_CHOICES), dict(CATEGORY_CHOICES), dict(TOPIC_CHOICES))
        name, email_address, message, location, category, topic, destination = (None, None, None, None, None, None, None)
        recipient_email, recipient_full_name = (None, None)

        for form in form_data:
            if 'location' in form.keys():
                location = locations[int(form['location'])]
            if 'enquiry_type' in form.keys():
                category = categories[int(form['enquiry_type'])]
            if 'enquiry_topic' in form.keys():
                topic = topics[int(form['enquiry_topic'])]
            if 'email_address' in form.keys():
                email_address = form['email_address']
            if 'name' in form.keys():
                name = form['name']
            if 'message' in form.keys():
                message = form['message']

        if topic == topics[2]:
            # Importing animals, plants or food, environmental regulations, sanitary and phytosanitary regulations
            recipient_email = "euexitDIT@defra.gov.uk"
            recipient_full_name = "DEFRA"

        elif topic == topics[3]:
            # Product safety and standards, packaging and labelling
            recipient_email = "enquiries@beis.gov.uk"
            recipient_full_name = "BEIS"

        elif topic == topics[4]:
            # Import controls, trade agreements, rules of origin
            destination = "Send to the DIT EU exit enquiries Zendesk - Susan Watersons Team"

        elif topic == topics[5]:
            # Help using the “Trade with the UK: look up tariffs, taxes and rules” service
            destination = """go to DDAT support team headed up by Madeline Lasko 
            (internal zendesk instance support@uktrade.zendesk.com
            same place as feedback we are using Forms API for)"""

        elif topic == topics[6]:
            # Other
            destination = "Send to the DIT EU exit enquiries Zendesk - Susan Watersons Team"

        form_data.append({'topic': topic, 'destination': destination})
        logger.debug(form_data)

        template = get_template('contact/contact_message_tmpl.txt')
        context = {
            'name': name,
            'email_address': email_address,
            'location': location,
            'category': category,
            'topic': topic,
            'message': message,
            'recipient_full_name': recipient_full_name
        }
        content = template.render(context)

        subject = "New UK Trade Helpdesk Enquiry"

        if topic in [topics[4], topics[5], topics[6]]:

            service_name = 'UK Trade Helpdesk'

            zendesk_form = ZendeskForm(data={
                'message': message,
                'email_address': email_address,
                'name': name
            })

            spam_control = helpers.SpamControl(
                contents=content
            )

            sender = helpers.Sender(
                email_address=email_address,
            )

            assert zendesk_form.is_valid()

            if settings.DIRECTORY_FORMS_API_BASE_URL:
                response = zendesk_form.save(
                    email_address=email_address,
                    full_name=name,
                    form_url='/contact/',
                    service_name=service_name,
                    spam_control=spam_control,
                    sender=sender,
                    subject=subject
                )

        else:

            headers = {'Reply-To': email_address}

            email = EmailMessage(
                subject,
                content,
                email_address,
                [recipient_email],
                headers=headers
            )
            email.send()

        return form_data






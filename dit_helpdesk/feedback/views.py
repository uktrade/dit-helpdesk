from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse
from feedback.forms import FeedbackForm, FeedbackFormStepOne, FeedbackFormStepTwo, FeedbackFormStepThree, \
    FeedbackFormStepFour, FeedbackFormStepFive, LOCATION_CHOICES, CATEGORY_CHOICES, TOPIC_CHOICES, ZendeskForm
import logging
from django.shortcuts import render, render_to_response
from formtools.wizard.views import SessionWizardView
logger = logging.getLogger(__name__)


FORMS = [("step_one", FeedbackFormStepOne),
         ("step_two", FeedbackFormStepTwo),
         ("step_three", FeedbackFormStepThree),
         ("step_four", FeedbackFormStepFour),
         ("step_five", FeedbackFormStepFive)]

TEMPLATES = {"step_one": "feedback/step_one.html",
             "step_two": "feedback/step_two.html",
             "step_three": "feedback/step_three.html",
             "step_four": "feedback/step_four.html",
             "step_five": "feedback/step_five.html"}


class FeedbackView(CreateView):
    """
    Generic class based View to create an instance of the data submitted in the feedback form
    """
    template_name = 'feedback_form.html'
    form_class = FeedbackForm

    def get_success_url(self):
        return reverse('feedback-success-view')


class FeedbackSuccessView(TemplateView):
    """
    Generic class based View for a successful form response
    """
    template_name = 'feedback_success.html'


class FeedbackFormWizardView(SessionWizardView):

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    form_list = FORMS

    def done(self, form_list, **kwargs):
        form_data = self.process_form_data(form_list)

        return render_to_response('feedback/done.html', {'form_data': form_data})

    @staticmethod
    def process_form_data(form_list):
        form_data = [form.cleaned_data for form in form_list]

        locations, categories, topics = (dict(LOCATION_CHOICES), dict(CATEGORY_CHOICES), dict(TOPIC_CHOICES))
        name, email_address, message, location, category, topic, destination = (None, None, None, None, None, None, None)

        print("form list: ", form_list)
        print("form data: ", form_data)
        print("topics: ", topics)

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

        print(name, email_address, message, location, category, topic )
        # check that service is working

        if topic == topics[1]:
            # Commodity codes, tariffs and measures, import procedures
            destination = "redirect to https://www.tax.service.gov.uk/shortforms/form/CITEX_CGEF"

        elif topic == topics[2]:
            # Importing animals, plants or food, environmental regulations, sanitary and phytosanitary regulations
            destination = "Submit form to DEFRA email address: euexitDIT@defra.gov.uk (pending approval)"
            recipient_email = "euexitDIT@defra.gov.uk"
            recipient_full_name = "DEFRA"

        elif topic == topics[3]:
            # Product safety and standards, packaging and labelling
            destination = "Submit form to BEIS email address - enquiries@beis.gov.uk"
            recipient_email = "enquiries@beis.gov.uk"
            recipient_full_name = "BEIS"

        elif topic == topics[4]:
            # Import controls, trade agreements, rules of origin
            destination = "Send to the DIT EU exit enquiries Zendesk - Susan Watersons Team"
            recipient_email = ""
            recipient_full_name = ""

        elif topic == topics[5]:
            # Help using the “Trade with the UK: look up tariffs, taxes and rules” service
            destination = """go to DDAT support team headed up by Madeline Lasko 
            (internal zendesk instance support@uktrade.zendesk.com
            same place as feedback we are using Forms API for)"""
            recipient_email = ""
            recipient_full_name = ""

        elif topic == topics[6]:
            # Other
            destination = "Send to the DIT EU exit enquiries Zendesk - Susan Watersons Team"
            recipient_email = ""
            recipient_full_name = ""

        form_data.append({'topic': topic, 'destination': destination})
        logger.debug(form_data)

        zendesk_form = ZendeskForm(data={
            'name': name,
            'email_address': email_address,
            'message': message
        })

        assert zendesk_form.is_valid()
        # zendesk_form.save(
        #     email_address=recipient_email,
        #     full_name=recipient_full_name,
        #     form_url='/feedback/',
        #     subject="Trade Helpdesk enquiry",
        #     service_name='Trade Helpdesk',
        # )
        print(dir(zendesk_form), zendesk_form.fields)

        return form_data






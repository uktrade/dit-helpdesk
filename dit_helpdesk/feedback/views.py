from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse
from feedback.forms import FeedbackForm


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

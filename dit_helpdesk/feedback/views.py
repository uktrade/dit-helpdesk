from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse
from feedback.forms import FeedbackForm


class FeedbackView(CreateView):
    template_name = 'feedback_form.html'
    form_class = FeedbackForm

    def get_success_url(self):
        return reverse('feedback-success-view')


class FeedbackSuccessView(TemplateView):
    template_name = 'feedback_success.html'

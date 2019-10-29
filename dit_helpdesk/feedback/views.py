from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from feedback.forms import FeedbackForm


class FeedbackView(FormView):
    """
    Generic class based View to create an instance of the data submitted in the feedback form
    """

    template_name = "feedback/feedback_form.html"
    form_class = FeedbackForm

    def get_success_url(self):
        return reverse("feedback-success-view")

    def form_valid(self, form):

        cleaned_data = form.cleaned_data

        template = get_template("feedback/feedback_email_tmpl.txt")
        context = {
            "name": cleaned_data["name"],
            "email": cleaned_data["email"],
            "message": cleaned_data["message"],
        }
        content = template.render(context)

        headers = {"Reply-To": cleaned_data["email"]}

        email = EmailMessage(
            "New Trade Helpdesk feedback",
            content,
            cleaned_data["email"],
            [settings.FEEDBACK_DESTINATION_EMAIL],
            headers=headers,
        )
        email.send()
        return super(FeedbackView, self).form_valid(form)


class FeedbackSuccessView(TemplateView):
    """
    Generic class based View for a successful form response
    """

    template_name = "feedback/feedback_success.html"

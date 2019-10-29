from django.urls import re_path

from contact import views

app_name = "contact"

urlpatterns = [
    # re_path(
    #     '',
    #     views.FeedbackView.as_view(),
    #     name='feedback-view'
    # ),
    #
    # re_path(
    #     'success/',
    #     views.FeedbackSuccessView.as_view(),
    #     name='feedback-success-view',
    # ),
    re_path("", views.ContactFormWizardView.as_view(), name="contact-view")
]

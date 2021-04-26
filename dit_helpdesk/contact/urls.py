from django.urls import re_path

from contact import views

app_name = "contact"

urlpatterns = [re_path("", views.ContactFormWizardView.as_view(), name="contact-view")]

from django.views.generic import TemplateView


class PrivacyTermsAndConditionsView(TemplateView):
    template_name = 'privacy_terms_and_conditions.html'

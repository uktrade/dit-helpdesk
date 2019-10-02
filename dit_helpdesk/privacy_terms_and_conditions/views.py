from django.views.generic import TemplateView


class PrivacyTermsAndConditionsView(TemplateView):
    """
    Generic class based template view for privacy nad conditions page

    """

    template_name = "privacy_terms_and_conditions.html"

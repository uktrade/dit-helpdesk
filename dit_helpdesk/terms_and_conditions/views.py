from django.views.generic import TemplateView


class TermsAndConditionsView(TemplateView):
    template_name = 'terms_and_conditions.html'

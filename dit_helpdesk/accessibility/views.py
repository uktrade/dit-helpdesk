from django.views.generic import TemplateView


class AccessibilityView(TemplateView):
    template_name = "accessibility/accessibility.html"

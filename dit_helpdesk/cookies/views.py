from django.views.generic import TemplateView


class CookiesView(TemplateView):
    template_name = "preferences.html"


class CookieDetailsView(TemplateView):
    template_name = "cookies.html"

from django.views.generic import TemplateView

class CookiesView(TemplateView):
    template_name = 'cookies/index.html'

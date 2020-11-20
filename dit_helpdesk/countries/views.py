from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.views import View
from django.views.generic.base import TemplateView

from .models import Country


def _country_has_agreement(country_code):
    agreements = dict(settings.AGREEMENTS)

    return agreements.get(country_code, False)


class ChooseCountryView(TemplateView):

    template_name = "countries/choose_country.html"
    redirect_to = "search:search-commodity-new"
    search_version = "new"

    countries = Country.objects.all()
    country_not_selected_summary_error_message = "Enter a country or territory"
    country_not_selected_input_error_message = "Enter a country or territory"

    def get(self, request, *args, **kwargs):
        context = {"country_options": [(c.country_code, c.name) for c in self.countries]}

        if "select-country" in request.GET:
            context["isError"] = True
            errorSummaryMessage = "Enter a country or territory"
            context["errorSummaryMessage"] = errorSummaryMessage
            context["errorInputMessage"] = errorSummaryMessage

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):

        origin_country = request.POST.get("origin_country", "").strip().upper()
        if (
                origin_country
                and Country.objects.filter(country_code=origin_country).exists()
        ):
            request.session["search_version"] = self.search_version

            if _country_has_agreement(origin_country):
                return redirect("agreement", country_code=origin_country.lower())

            return redirect(self.redirect_to, country_code=origin_country.lower())
        else:
            context = {
                "country_options": [(c.country_code, c.name) for c in self.countries],
                "isError": True,
                "errorSummaryMessage": self.country_not_selected_summary_error_message,
                "errorInputMessage": self.country_not_selected_input_error_message,
            }
            return self.render_to_response(context)


class ChooseCountryOldView(ChooseCountryView):

    redirect_to = "search:search-commodity"
    search_version = "old"


class AgreementView(View):

    def get(self, request, *args, **kwargs):
        country_code = kwargs["country_code"].upper()
        try:
            country = Country.objects.get(country_code=country_code)
        except Country.DoesNotExist:
            raise Http404

        if not _country_has_agreement(country.country_code):
            raise Http404

        return HttpResponse("OK")

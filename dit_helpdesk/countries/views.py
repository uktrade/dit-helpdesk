from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

from .models import Country


def _has_agreement(country_code):
    agreements = dict(settings.AGREEMENTS)

    return agreements.get(country_code, False)


class ChooseCountryView(TemplateView):

    template_name = "countries/choose_country.html"
    redirect_to = "search:search-commodity"
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
            request.session["origin_country"] = origin_country

            if _has_agreement(origin_country):
                return redirect("country-information", country_code=origin_country.lower())

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


class CountryInformationView(TemplateView):
    template_name = "countries/information.html"

    def get(self, request, *args, **kwargs):
        country_code = kwargs["country_code"].upper()
        try:
            country = Country.objects.get(country_code=country_code)
        except Country.DoesNotExist:
            raise Http404

        if not _has_agreement(country.country_code):
            raise Http404

        self.country = country

        return super().get(request, *args, **kwargs)

    def _get_template_name(self, country, template_name):
        return f"countries/{country.country_code}/_{template_name}.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        country = self.country

        ctx["country"] = country
        ctx["country_code"] = country.country_code.lower()

        ctx["trade_agreements_template_name"] = self._get_template_name(country, "trade_agreements")
        ctx["goods_template_name"] = self._get_template_name(country, "goods")
        ctx["grow_your_business_template_name"] = self._get_template_name(country, "grow_your_business")
        ctx["other_information_template_name"] = self._get_template_name(country, "other_information")

        return ctx

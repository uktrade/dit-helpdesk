from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic.base import TemplateView

from .models import Country


def _has_agreement(country_code):
    agreements = dict(settings.AGREEMENTS)

    has_agreement = agreements.get(country_code, False)

    if callable(has_agreement):
        has_agreement = has_agreement()

    return has_agreement


class ChooseCountryView(TemplateView):
    template_name = "countries/choose_country.html"
    redirect_to = "search:search-commodity"
    search_version = "new"

    countries = Country.objects.all()
    country_not_selected_summary_error_message = "Enter a country or territory"
    country_not_selected_input_error_message = "Enter a country or territory"

    def get(self, request, *args, **kwargs):
        context = {
            "country_options": [(c.country_code, c.name) for c in self.countries]
        }

        if "select-country" in request.GET:
            context["isError"] = True
            errorSummaryMessage = "Enter a country or territory"
            context["errorSummaryMessage"] = errorSummaryMessage
            context["errorInputMessage"] = errorSummaryMessage

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        error_context = {
            "country_options": [(c.country_code, c.name) for c in self.countries],
            "isError": True,
            "errorSummaryMessage": self.country_not_selected_summary_error_message,
            "errorInputMessage": self.country_not_selected_input_error_message,
        }

        origin_country = request.POST.get("origin_country", "").strip().upper()
        if not origin_country:
            return self.render_to_response(error_context)

        try:
            country = Country.objects.get(country_code=origin_country)
        except Country.DoesNotExist:
            return self.render_to_response(error_context)

        request.session["search_version"] = self.search_version
        request.session["origin_country"] = origin_country

        if _has_agreement("EU" if country.is_eu else origin_country):
            return redirect("country-information", country_code=origin_country.lower())

        return redirect(self.redirect_to, country_code=origin_country.lower())


class ChooseCountryOldView(ChooseCountryView):

    redirect_to = "search:search-commodity"
    search_version = "old"


class CountryInformationView(TemplateView):
    def get(self, request, *args, **kwargs):
        country_code = kwargs["country_code"].upper()
        try:
            country = Country.objects.get(country_code=country_code)
        except Country.DoesNotExist:
            raise Http404

        self.origin_country = country

        if country.is_eu:
            country = Country.objects.get(country_code="EU")

        if not _has_agreement(country.country_code):
            raise Http404

        self.country = country
        self.country_code = country.country_code

        return super().get(request, *args, **kwargs)

    def get_template_names(self):
        """This is called by render_to_response"""
        return [f"countries/{self.country_code}/information.html"]

    def _get_template_name(self, country_code, template_name):
        return f"countries/{country_code}/_{template_name}.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        country = self.country

        ctx["original_country"] = self.origin_country
        ctx["country"] = country
        ctx["country_name"] = (
            "the European Union" if country.country_code == "EU" else country.name
        )

        # Cleanup - TC-1036 - change "new_scenario" to "scenario" once migration to cleanup DB is complete
        # Information Sharing section is one of 2 scenario templates, not country based, so pass
        # "information" instead of "country_code" to access the correct sub-folder
        ctx["information_sharing_template_name"] = self._get_template_name(
            "information",
            f"information_sharing_{settings.TRADE_AGREEMENT_TEMPLATE_MAPPING[country.new_scenario]}_IS",
        )
        ctx["trade_agreements_template_name"] = self._get_template_name(
            self.country_code, "trade_agreements"
        )
        ctx["goods_template_name"] = self._get_template_name(self.country_code, "goods")
        ctx["grow_your_business_template_name"] = self._get_template_name(
            self.country_code, "grow_your_business"
        )
        ctx["other_information_template_name"] = self._get_template_name(
            self.country_code, "other_information"
        )

        return ctx


class LocationAutocompleteView(View):
    def _get_country_graph_item(self, country):
        return {
            "names": {"en-GB": country.name},
            "meta": {"canonical": True, "canonical-mask": 1, "stable-name": True},
            "edges": {"from": []},
        }

    def _get_country_graph_synonym_item(self, country, synonym):
        return {
            "names": {"en-GB": synonym},
            "meta": {"canonical": False, "canonical-mask": 1, "stable-name": True},
            "edges": {"from": [country.country_code.lower()]},
        }

    def get(self, request):
        to_remove = settings.COUNTRIES_TO_REMOVE

        countries = Country.objects.exclude(country_code__in=to_remove)

        response = {}
        for country in countries:
            country_code = country.country_code
            response[country_code.lower()] = self._get_country_graph_item(country)

            synonyms = settings.COUNTRY_SYNONYMS.get(country_code, [])
            for synonym in synonyms:
                response[
                    f"nym:{synonym.lower()}"
                ] = self._get_country_graph_synonym_item(country, synonym)

        return JsonResponse(response)

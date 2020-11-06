from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.base import TemplateView

from countries.models import Country


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

            return redirect(
                reverse(
                    self.redirect_to,
                    kwargs={"country_code": origin_country.lower()},
                )
            )
        else:
            context = {
                "country_options": [(c.country_code, c.name) for c in self.countries],
                "isError": True,
                "errorSummaryMessage": self.country_not_selected_summary_error_message,
                "errorInputMessage": self.country_not_selected_input_error_message,
            }
            return self.render_to_response(context)


class ChooseCountryOldView(ChooseCountryView):

    redirect_to = "search:search-commodity-old"
    search_version = "old"


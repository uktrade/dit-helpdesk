from django.contrib.messages.context_processors import get_messages
from django.shortcuts import render, redirect
from django.urls import reverse

from countries.models import Country


def choose_country_view(request):

    countries = Country.objects.all()
    country_not_selected_summary_error_message = "Enter a country"
    country_not_selected_input_error_message = "Enter a country"

    try:
        del request.session["origin_country"]
    except KeyError:
        pass

    if request.method == "POST":
        origin_country = request.POST.get("origin_country", "").strip().upper()
        if (
            origin_country
            and Country.objects.filter(country_code=origin_country).exists()
        ):
            request.session["origin_country"] = origin_country
            return redirect(
                reverse(
                    "search:search-commodity",
                    kwargs={"country_code": origin_country.lower()},
                )
            )
        else:
            context = {
                "country_options": [(c.country_code, c.name) for c in countries],
                "isError": True,
                "errorSummaryMessage": country_not_selected_summary_error_message,
                "errorInputMessage": country_not_selected_input_error_message,
            }
            return render(request, "countries/choose_country.html", context)

    context = {"country_options": [(c.country_code, c.name) for c in countries]}

    errorSummaryMessage = "Enter a country"
    if errorSummaryMessage in [message.message for message in get_messages(request)]:
        context["isError"] = True
        context["errorSummaryMessage"] = errorSummaryMessage
        context["errorInputMessage"] = errorSummaryMessage

    return render(request, "countries/choose_country.html", context)

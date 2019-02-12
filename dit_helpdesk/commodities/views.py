import json
import re

# from django.views.decorators.cache import cache_page
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest #HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

from commodities.models import Commodity
from countries.models import Country

def commodity_detail(request, commodity_code):

    selected_country = request.session.get('origin_country', '').upper()

    country = Country.objects.filter(
        country_code=selected_country
    )

    country_exists = False

    country_name = country.values()[0]['name']

    if selected_country:
        country_exists = country.exists()

    if (not selected_country) or (not country_exists):
        messages.error(request, 'Invalid originCountry')
        return redirect(reverse('choose-country'))

    commodity = get_object_or_404(
        Commodity, commodity_code=commodity_code,
    )

    commodity_code_regex = re.search('([0-9]{2})([0-9]{2})([0-9]{6})', commodity.commodity_code)

    commodity_code_split = [
        commodity_code_regex.group(1),
        commodity_code_regex.group(2),
        commodity_code_regex.group(3)
    ]

    context = {
        'selected_origin_country': selected_country,
        'selected_origin_country_name': country_name,
        'commodity': commodity,
        'commodity_code': commodity_code_split
    }

    return render(request, 'commodities/commodity_detail.html', context)


def get_measure_table_data(request, commodity_code, origin_country):

    if not Country.objects.filter(country_code=origin_country).exists():
        raise HttpResponseBadRequest('invalid originCountry code')

    commodity = get_object_or_404(
        Commodity, commodity_code=commodity_code,
    )
    import_measures = commodity.tts_obj.get_import_measures(origin_country)

    table_data = [
        measure_json.get_vue_table_dict() for measure_json in import_measures
    ]
    table_data.sort(key=lambda di: di['table_rank'])

    return JsonResponse({'gridData': table_data})

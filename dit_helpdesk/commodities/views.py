import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

from commodities.models import Commodity
from countries.models import Country
from trade_tariff_service.tts_api import COMMODITY_DETAIL_TABLE_KEYS
from rules_of_origin.util import get_rules_of_origin_html_fragments

TABLE_COLUMN_TITLES = [
    tup[1] for tup in COMMODITY_DETAIL_TABLE_KEYS
]

COMMODITY_URL = (
    'https://www.trade-tariff.service.gov.uk/trade-tariff/'
    'commodities/%s.json?currency=EUR&day=1&month=1&year=2019'
)

def commodity_detail(request, commodity_code, country_code):

    selected_country = country_code.upper()

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

    url = COMMODITY_URL % commodity.commodity_code
    try:
        resp = requests.get(url, timeout=10)
    except requests.exceptions.ReadTimeout:
        return None
    resp_content = resp.content.decode()
    if resp.status_code == 200:
        commodity.tts_json = resp_content
        commodity.save()

    table_data = []
    try:
        import_measures = commodity.tts_obj.get_import_measures(selected_country)
        table_data = [
            measure_json.get_table_row() for measure_json in import_measures
        ]
    except:
        print("No Measures")

    context = {
        'selected_origin_country': selected_country,
        'commodity': commodity,
        'selected_origin_country_name': country_name,
        'roo_fragments': get_rules_of_origin_html_fragments(commodity),
        'table_data': table_data,
        'column_titles': TABLE_COLUMN_TITLES,
    }

    return render(request, 'commodities/commodity_detail.html', context)

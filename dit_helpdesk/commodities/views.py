import json
from datetime import datetime, timedelta, timezone

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

HEADING_URL = (
    'https://www.trade-tariff.service.gov.uk/trade-tariff/'
    'headings/%s.json?currency=EUR&day=1&month=1&year=2019'
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

    if commodity.last_updated > datetime.now(timezone.utc) - timedelta(days=1) or commodity.tts_json is None:

        get_commodity_content(commodity)

    table_data = []

    import_measures = commodity.tts_obj.get_import_measures(selected_country)
    table_data = [
        measure_json.get_table_row() for measure_json in import_measures
    ]

    context = {
        'selected_origin_country': selected_country,
        'commodity': commodity,
        'selected_origin_country_name': country_name,
        'roo_fragments': get_rules_of_origin_html_fragments(commodity),
        'table_data': table_data,
        'column_titles': TABLE_COLUMN_TITLES,
        'regulations': commodity.regulation_set.all()
    }

    return render(request, 'commodities/commodity_detail.html', context)


def get_commodity_content(commodity):

    url = COMMODITY_URL % commodity.commodity_code
    resp = requests.get(url, timeout=10)
    resp_content = None
    if resp.status_code == 200:
        resp_content = resp.content.decode()
    elif resp.status_code == 404:
        url = HEADING_URL % commodity.commodity_code[:4]
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            resp_content = resp.content.decode()

    resp_content = update_tts_json_measure_conditions(resp_content)
    commodity.tts_json = resp_content
    commodity.save()


def update_tts_json_measure_conditions(resp_content):

    obj = json.loads(resp_content)
    for idx, measure in enumerate(obj['import_measures']):
        measure['measure_id'] = idx
        for i, condition in enumerate(measure['measure_conditions']):
            if isinstance(condition, dict):
                condition['measure_id'] = idx
                condition['condition_id'] = i
    return json.dumps(obj)

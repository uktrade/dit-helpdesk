# -----------------------------------------------------------------------------
# NOTE - table column headers.
# -----------------------------------------------------------------------------
# If the table columns headings are changed, they also need to be updated in
# the SCSS file `_flexible-tables.scss` - otherwise the card-based layout for
# smaller screens will break.
# -----------------------------------------------------------------------------

import os
import json
from datetime import datetime, timedelta, timezone

import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

from commodities.models import Commodity
from countries.models import Country
from rules_of_origin.models import RulesGroupMember
from trade_tariff_service.tts_api import COMMODITY_DETAIL_TABLE_KEYS
from rules_of_origin.util import get_rules_of_origin_html_fragments

import logging
import sys
sys.setrecursionlimit(1000000)


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

HIERARCHY_JSON_PATH = os.path.join(os.path.dirname(__file__), '../hierarchy/hierarchy_cached.json')
with open(HIERARCHY_JSON_PATH) as f:
    HIERARCHY_CACHED = json.loads(f.read())

def commodity_detail(request, commodity_code, country_code):
    commodity_path = get_commodity_path(HIERARCHY_CACHED, commodity_code)
    commodity_path = format_path(commodity_path)

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

    # rules = list(commodity.get_heading().chapter.rules_of_origin.all())
    rules = []
    try:
        for country_code in country:
            for rd in country_code.rulesgroupmember_set.first().rules_group.rulesdocument_set.all():
                for r in rd.rule_set.all():
                    if r.chapter == commodity.get_heading().chapter:
                        rules.append(r)
    except Exception as ex:
        print(ex.args)

    context = {
        'selected_origin_country': selected_country,
        'commodity': commodity,
        'selected_origin_country_name': country_name,
        'rules_of_origin': rules,
        'table_data': table_data,
        'column_titles': TABLE_COLUMN_TITLES,
        'regulations': commodity.regulation_set.all(),
        'commodity_path': commodity_path
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


def measure_condition_detail(request, commodity_code, country_code, measure_id):

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

    commodity = Commodity.objects.get(commodity_code=commodity_code)
    import_measure = commodity.tts_obj.get_import_measure_by_id(int(measure_id), country_code=selected_country)
    conditions = import_measure.get_measure_conditions_by_measure_id(int(measure_id))

    context = {
        'selected_origin_country': selected_country,
        'commodity': commodity,
        'selected_origin_country_name': country_name,
        'import_measure': import_measure,
        'conditions': conditions
    }

    return render(request, 'commodities/measure_condition_detail.html', context)

def get_commodity_path(json_tree, target_commodity_code):
    if 'commodity_code' in json_tree and  json_tree['commodity_code'] == target_commodity_code:
        return json_tree['name']
    else:
        for attr, value in json_tree.items():
            if attr == 'children':
                for dic in value:
                    p = get_commodity_path(dic, target_commodity_code)
                    if p:
                        return json_tree['name'] + ': ' +  p

def format_path(commodity_path):
    commodity_path = commodity_path.replace("root: ", "")
    commodity_path = commodity_path.replace("H: ", "")
    commodity_path = commodity_path.replace("I - ", "")
    return commodity_path

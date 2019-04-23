# -----------------------------------------------------------------------------
# NOTE - table column headers.
# -----------------------------------------------------------------------------
# If the table columns headings are changed, they also need to be updated in
# the SCSS file `_flexible-tables.scss` - otherwise the card-based layout for
# smaller screens will break.
# -----------------------------------------------------------------------------

import json
import re
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
from hierarchy.models import SubHeading, Heading, Chapter, Section

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

    if commodity.last_updated < datetime.now(timezone.utc) - timedelta(days=1) or commodity.tts_json is None:
        get_commodity_content(commodity)

    table_data = []

    import_measures = commodity.tts_obj.get_import_measures(selected_country)
    table_data = [
        measure_json.get_table_row() for measure_json in import_measures
    ]

    rules = []
    roo_footnotes = None

    try:
        for country_code in country:
            rules_document = country_code.rulesgroupmember_set.first().rules_group.rulesdocument_set.all()
            for doc in rules_document:
                roo_footnotes = doc.footnotes.all().order_by('id')
            for rd in country_code.rulesgroupmember_set.first().rules_group.rulesdocument_set.all():
                for r in rd.rule_set.all().order_by('id'):
                    if r.chapter == commodity.get_heading().chapter:
                        rules.append(r)
    except Exception as ex:
        print(ex.args)

    regulations = commodity.regulation_set.all()
    if not regulations and commodity.parent_subheading:
        regulations = commodity.parent_subheading.regulation_set.all()

    commodity_path = commodity.get_path()
    accordion_title = commodity_hierarchy_section_header(commodity_path)

    context = {
        'selected_origin_country': selected_country,
        'commodity': commodity,
        'selected_origin_country_name': country_name,
        'rules_of_origin': rules,
        'roo_footnotes': roo_footnotes,
        'table_data': table_data,
        'column_titles': TABLE_COLUMN_TITLES,
        'regulations': regulations,
        'accordion_title': accordion_title,
        'commodity_hierarchy_context': commodity_hierarchy_context(commodity_path, selected_country, commodity_code)
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

def commodity_hierarchy_context(commodity_path, country_code, commodity_code):
    listSize = len(commodity_path) - 1
    html = ''
    reversedList =  reversed(commodity_path)
    for index, lista in enumerate(reversedList):

        if index is 0:
            # We dont want to retrieve section as it is explicity renders by commodity_hierarchy_section_header
            html += ''
        else:
            html +=  f'<ul id="hierarchy-tree-list-{index}" class="app-hierarchy-tree--child">'

            for i, item in enumerate(lista) :
                expand = 'open'
                if index is listSize:
                    expand = 'closed'

                if type(item) is Commodity:
                    if item.commodity_code == commodity_code:
                        html += f"""
                            <li id="tree-list-{index}-item-{i}" class="app-hierarchy-tree__part app-hierarchy-tree__commodity">
                                <span class="govuk-!-font-weight-bold app-hierarchy-tree__link">{item.tts_title}</span><span class="govuk-visually-hidden"> &ndash; </span>{_generate_commodity_code_html(item)}
                            </li>
                            """
                    else:
                        html += f"""
                            <li id="tree-list-{index}-item-{i}" class="app-hierarchy-tree__part app-hierarchy-tree__commodity">
                                <a href="{item.get_absolute_url(country_code)}" class="app-hierarchy-tree__link app-hierarchy-tree__link--child">
                                <span>{item.tts_title}</span><span class="govuk-visually-hidden"> &ndash; </span></a>{_generate_commodity_code_html(item)}
                            </li>
                            """

                elif hasattr(item,'description'):
                    html += f"""
                        <li id="tree-list-{index}-item-{i}" class="app-hierarchy-tree__part app-hierarchy-tree__chapter app-hierarchy-tree__parent--{expand}">
                            <a href="{item.get_hierarchy_url(country_code)}#{item.hierarchy_key}" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">{item.description.capitalize()}</a>{_generate_commodity_code_html(item)}"""
                    if index is listSize:
                        html += '</li>'

            if index is listSize:
                for i in range(0, listSize):
                    # close
                    html += '</ul>'

    return html

def _generate_commodity_code_html(item):
    commodity_code_html = ''
    if (type(item) is not Section):
        commodity_code_html = '<span class="app-commodity-code app-hierarchy-tree__commodity-code">'

        if type(item) is Commodity:
            item.harmonized_code = item.commodity_code

        code_regex = re.search('([0-9]{6})([0-9]{2})([0-9]{2})', item.harmonized_code)
        code_split = [
            code_regex.group(1),
            code_regex.group(2),
            code_regex.group(3)
        ]

        for index, code_segment in enumerate(code_split):
            counter = str(int(index) + 1)
            commodity_code_html = commodity_code_html + \
                '<span class="app-commodity-code__highlight app-commodity-code__highlight--' + counter + '">' + code_segment + '</span>'

        commodity_code_html = commodity_code_html + '</span>'
    return  commodity_code_html

def commodity_hierarchy_section_header(reversed_commodity_tree):
    section_index = len(reversed_commodity_tree) - 1
    item = reversed_commodity_tree[section_index][0]
    html = f'Section {item.roman_numeral}: {item.title.capitalize()}'
    return html

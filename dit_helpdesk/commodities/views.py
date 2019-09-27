# -----------------------------------------------------------------------------
# NOTE - table column headers.
# -----------------------------------------------------------------------------
# If the table columns headings are changed, they also need to be updated in
# the SCSS file `_flexible-tables.scss` - otherwise the card-based layout for
# smaller screens will break.
# -----------------------------------------------------------------------------

import re
from datetime import datetime, timedelta, timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

from commodities.models import Commodity
from countries.models import Country
from trade_tariff_service.tts_api import COMMODITY_DETAIL_TABLE_KEYS
from hierarchy.models import Section

TABLE_COLUMN_TITLES = [
    tup[1] for tup in COMMODITY_DETAIL_TABLE_KEYS
]


def commodity_detail(request, commodity_code, country_code):
    """
    View for the commodity detail page template which takes two arguments; the 10 digit code for the commodity to
    display and the two character country code to provide the exporter geographical context which is
    used to display the appropriate related supporting content

    :param request: django http request object
    :param commodity_code: string
    :param country_code: string
    :return:
    """

    country = Country.objects.filter(
        country_code=country_code.upper()
    ).first()

    if not country:
        messages.error(request, 'Invalid originCountry')
        return redirect(reverse('choose-country'))

    commodity = get_object_or_404(
        Commodity, commodity_code=commodity_code,
    )

    if commodity.last_updated < datetime.now(timezone.utc) - timedelta(days=1) or commodity.tts_json is None:
        commodity.update_content()

    import_measures = commodity.tts_obj.get_import_measures(country.country_code)
    table_data = [
        measure_json.get_table_row() for measure_json in import_measures
    ]

    commodity_path = commodity.get_path()
    accordion_title = commodity_hierarchy_section_header(commodity_path)
    rules_of_origin = commodity.get_rules_of_origin(country_code=country.country_code)

    context = {
        'selected_origin_country': country.country_code,
        'commodity': commodity,
        'selected_origin_country_name': country.name,
        'rules_of_origin': rules_of_origin,
        'roo_footnotes': rules_of_origin,
        'table_data': table_data,
        'column_titles': TABLE_COLUMN_TITLES,
        'regulations': commodity.get_regulations(),
        'accordion_title': accordion_title,
        'commodity_hierarchy_context': commodity_hierarchy_context(commodity_path, country.country_code, commodity_code)
    }

    return render(request, 'commodities/commodity_detail.html', context)


def measure_condition_detail(request, commodity_code, country_code, measure_id):
    """
    View for an individual measure condition detail page template which takes three arguments, the commodity code that
    the measure belongs to, the measure id of the individual measure being presented and the country code to
    provide the exporter geographical context
    :param request: django http request object
    :param commodity_code: string
    :param country_code: string
    :param measure_id: int
    :return:
    """

    country = Country.objects.filter(
        country_code=country_code.upper()
    ).first()

    if not country:
        messages.error(request, 'Invalid originCountry')
        return redirect(reverse('choose-country'))

    commodity = Commodity.objects.get(commodity_code=commodity_code)
    import_measure = commodity.tts_obj.get_import_measure_by_id(int(measure_id), country_code=country_code)
    conditions = import_measure.get_measure_conditions_by_measure_id(int(measure_id))

    context = {
        'selected_origin_country': country.country_code,
        'commodity': commodity,
        'selected_origin_country_name': country.name,
        'import_measure': import_measure,
        'conditions': conditions
    }

    return render(request, 'commodities/measure_condition_detail.html', context)


def commodity_hierarchy_context(commodity_path, country_code, commodity_code):
    """
    View helper function that returns an html representation of the context of the commodity within the
    hierarchy takes three arguments: the path to the commodity, the country code of the exporting country and the
    commodity code
    :param commodity_path: string
    :param country_code: string
    :param commodity_code: string
    :return: html
    """
    listSize = len(commodity_path)
    html = ''
    reversedList = reversed(commodity_path)

    for index, lista in enumerate(reversedList):
        if index is 0:
            # We dont want to retrieve section as it is explicity renders by commodity_hierarchy_section_header
            html += ''
        else:
            html += f'<ul id="hierarchy-tree-list-{index}" class="app-hierarchy-tree--child">'
            for i, item in enumerate(lista):
                expand = 'open'
                if index is listSize:
                    expand = 'closed'

                if type(item) is Commodity:
                    if item.commodity_code == commodity_code:
                        html += f"""
                            <li id="tree-list-{index}-item-{i}" class="app-hierarchy-tree__part app-hierarchy-tree__commodity">
                                <span class="govuk-!-font-weight-bold app-hierarchy-tree__link">{item.description}</span><span class="govuk-visually-hidden"> &ndash; </span>{_generate_commodity_code_html(item)}
                            </li>
                            """
                    else:
                        html += f"""
                           <li id="tree-list-{index}-item-{i}" class="app-hierarchy-tree__part app-hierarchy-tree__commodity">
                                <a href="{item.get_absolute_url(country_code)}" class="app-hierarchy-tree__link app-hierarchy-tree__link--child">
                                <span>{item.description}</span><span class="govuk-visually-hidden"> &ndash; </span></a>{_generate_commodity_code_html(item)}
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
    """
    View helper function that genrates an html representation of the ten digit commodity code broken into three groups
    of 6, 2 and  digits and colour code formatted
    :param item: model instance
    :return: html
    """
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
    return commodity_code_html


def commodity_hierarchy_section_header(reversed_commodity_tree):
    """
    View helper function to extract the Section Numeral and title for the hierarchy context of the commodity
    and returned as formatted html string
    :param reversed_commodity_tree: list
    :return: html
    """
    section_index = len(reversed_commodity_tree) - 1
    section = reversed_commodity_tree[section_index][0]
    html = f'Section {section.roman_numeral}: {section.title.capitalize()}'
    return html

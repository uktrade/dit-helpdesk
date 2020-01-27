# -----------------------------------------------------------------------------
# NOTE - table column headers.
# -----------------------------------------------------------------------------
# If the table columns headings are changed, they also need to be updated in
# the SCSS file `_flexible-tables.scss` - otherwise the card-based layout for
# smaller screens will break.
# -----------------------------------------------------------------------------

import re
from datetime import datetime, timedelta, timezone
from pprint import pprint

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages

from commodities.models import Commodity
from countries.models import Country
from hierarchy.views import get_hierarchy_context
from hierarchy.models import Section, Chapter, Heading, SubHeading

from hierarchy.helpers import (
    TABLE_COLUMN_TITLES,
    get_nomenclature_group_measures,
    get_back_link_url,
)


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

    country = Country.objects.filter(country_code=country_code.upper()).first()

    if not country:
        messages.error(request, "Invalid originCountry")
        return redirect(reverse("choose-country"))

    commodity = get_object_or_404(Commodity, commodity_code=commodity_code)

    if (
        commodity.last_updated < datetime.now(timezone.utc) - timedelta(days=1)
        or commodity.tts_json is None
    ):
        commodity.update_content()

    modals_dict = {}

    tariffs_and_charges_measures = get_nomenclature_group_measures(
        commodity, "Tariffs and charges", country.country_code
    )
    tariffs_and_charges_table_data = [
        measure_json.get_table_row()
        for measure_json in tariffs_and_charges_measures
        if measure_json.vat or measure_json.excise
    ]
    for measure_json in tariffs_and_charges_measures:
        modals_dict.update(measure_json.measures_modals)

    quotas_measures = get_nomenclature_group_measures(
        commodity, "Quotas", country.country_code
    )

    quotas_table_data = [
        measure_json.get_table_row() for measure_json in quotas_measures
    ]
    for measure_json in quotas_measures:
        modals_dict.update(measure_json.measures_modals)

    other_measures = get_nomenclature_group_measures(
        commodity, "Other measures", country.country_code
    )
    other_table_data = [measure_json.get_table_row() for measure_json in other_measures]
    for measure_json in other_measures:
        modals_dict.update(measure_json.measures_modals)

    commodity_path = commodity.get_path()
    accordion_title = commodity_hierarchy_section_header(commodity_path)
    rules_of_origin = commodity.get_rules_of_origin(country_code=country.country_code)

    heading = commodity.get_heading()
    chapter = heading.chapter
    section = chapter.section

    context = {
        "back_link_url": get_back_link_url(country_code, request),
        "selected_origin_country": country.country_code,
        "commodity": commodity,
        "selected_origin_country_name": country.name,
        "rules_of_origin": rules_of_origin,
        "roo_footnotes": rules_of_origin,
        "tariffs_and_charges_table_data": tariffs_and_charges_table_data,
        "quotas_table_data": quotas_table_data,
        "other_table_data": other_table_data,
        "column_titles": TABLE_COLUMN_TITLES,
        "regulations": commodity.get_regulations(),
        "accordion_title": accordion_title,
        "commodity_notes": commodity.tts_obj.footnotes,
        "chapter_notes": chapter.chapter_notes,
        "heading_notes": heading.heading_notes,
        "section_notes": section.section_notes,
        "commodity_hierarchy_context": get_hierarchy_context(
            commodity_path, country.country_code, commodity_code, commodity
        ),
        "modals": modals_dict,
        "is_eu_member": country_code.upper() == "EU",
    }

    return render(request, "commodities/commodity_detail.html", context)


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

    country = Country.objects.filter(country_code=country_code.upper()).first()

    if not country:
        messages.error(request, "Invalid originCountry")
        return redirect(reverse("choose-country"))

    commodity = Commodity.objects.get(commodity_code=commodity_code)
    import_measure = commodity.tts_obj.get_import_measure_by_id(
        int(measure_id), country_code=country_code
    )
    conditions = import_measure.get_measure_conditions_by_measure_id(int(measure_id))

    context = {
        "selected_origin_country": country.country_code,
        "commodity_code": commodity.commodity_code,
        "commodity_description": commodity.description,
        "selected_origin_country_name": country.name,
        "conditions": conditions,
        "commodity_code_split": commodity.commodity_code_split,
        "measure_type": import_measure.type_description,
        "column_headers": [
            "Condition code",
            "Condition",
            "Document code",
            "Requirement",
            "Action",
            "Duty",
        ],
    }

    return render(request, "commodities/measure_condition_detail.html", context)


def measure_quota_detail(
    request, commodity_code, country_code, measure_id, order_number
):
    """
    View for an individual measure condition detail page template which takes three arguments, the commodity code that
    the measure belongs to, the measure id of the individual measure being presented and the country code to
    provide the exporter geographical context
    :param request: django http request object
    :param commodity_code: string
    :param country_code: string
    :param measure_id: int
    :param order_number: string
    :return:
    """

    country = Country.objects.filter(country_code=country_code.upper()).first()

    if not country:
        messages.error(request, "Invalid originCountry")
        return redirect(reverse("choose-country"))

    commodity = Commodity.objects.get(commodity_code=commodity_code)
    import_measure = commodity.tts_obj.get_import_measure_by_id(
        int(measure_id), country_code=country_code
    )
    conditions = import_measure.get_measure_conditions_by_measure_id(int(measure_id))
    quota_def = import_measure.get_measure_quota_definition_by_order_number(
        order_number
    )
    geographical_area = import_measure.get_geographical_area()

    context = {
        "selected_origin_country": country.country_code,
        "commodity_description": commodity.description,
        "commodity_code": commodity.commodity_code,
        "selected_origin_country_name": country.name,
        "quota_def": quota_def,
        "geographical_area": geographical_area,
        "commodity_code_split": commodity.commodity_code_split,
        "measure_type": import_measure.type_description,
    }

    return render(request, "commodities/measure_quota_detail.html", context)


def commodity_hierarchy_section_header(reversed_commodity_tree):
    """
    View helper function to extract the Section Numeral and title for the hierarchy context of the commodity
    and returned as formatted html string
    :param reversed_commodity_tree: list
    :return: html
    """
    section_index = len(reversed_commodity_tree) - 1
    section = reversed_commodity_tree[section_index][0]
    html = f"Section {section.roman_numeral}: {section.title.capitalize()}"
    return html

# -----------------------------------------------------------------------------
# NOTE - table column headers.
# -----------------------------------------------------------------------------
# If the table columns headings are changed, they also need to be updated in
# the SCSS file `_flexible-tables.scss` - otherwise the card-based layout for
# smaller screens will break.
# -----------------------------------------------------------------------------


from django.conf import settings
from django.contrib import messages
from django.http.response import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView

from countries.models import Country

from hierarchy.helpers import (
    get_nomenclature_group_measures,
    TABLE_COLUMN_TITLES,
)
from hierarchy.views import get_hierarchy_context
from regulations.models import RegulationGroup

from .models import Commodity
from .helpers import get_tariff_content_context


class BaseCommodityDetailView(TemplateView):

    def get(self, request, *args, **kwargs):
        country_code = kwargs["country_code"]
        try:
            self.country = Country.objects.get(country_code=country_code.upper())
        except Country.DoesNotExist:
            messages.error(request, "Invalid originCountry")
            return redirect("choose-country")

        commodity_code = kwargs["commodity_code"]
        goods_nomenclature_sid = kwargs["nomenclature_sid"]
        try:
            self.commodity = Commodity.objects.get(
                commodity_code=commodity_code,
                goods_nomenclature_sid=goods_nomenclature_sid,
            )
        except Commodity.DoesNotExist:
            raise Http404

        if self.commodity.should_update_content():
            self.commodity.update_content()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        commodity = self.commodity
        country = self.country

        ctx["selected_origin_country"] = country.country_code
        ctx["selected_origin_country_name"] = country.name

        commodity_path = commodity.get_path()
        ctx["accordion_title"] = commodity_hierarchy_section_header(commodity_path)
        ctx["commodity_hierarchy_context"] = get_hierarchy_context(
            commodity_path,
            country.country_code,
            commodity.commodity_code,
            commodity,
        )
        ctx["commodity"] = commodity

        heading = commodity.get_heading()
        chapter = heading.chapter
        section = chapter.section
        ctx["commodity_notes"] = commodity.tts_obj.footnotes
        ctx["chapter_notes"] = chapter.chapter_notes
        ctx["heading_notes"] = heading.heading_notes
        ctx["section_notes"] = section.section_notes

        return ctx


class CommodityDetailView(BaseCommodityDetailView):

    def get_template_names(self):
        if settings.UKGT_ENABLED:
            template = "commodities/commodity_detail_ukgt.html"
        else:
            template = "commodities/commodity_detail.html"

        return template

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        country = self.country
        commodity = self.commodity

        modals_dict = {}

        tariffs_and_charges_measures = get_nomenclature_group_measures(
            commodity, "Tariffs and charges", country.country_code
        )
        tariffs_and_charges_table_data = (
            [
                measure_json.get_table_row()
                for measure_json in tariffs_and_charges_measures
                if measure_json.vat or measure_json.excise
            ]
            if country.country_code.upper() == "EU"
            else [
                measure_json.get_table_row()
                for measure_json in tariffs_and_charges_measures
            ]
        )

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

        rules_of_origin = commodity.get_rules_of_origin(country_code=country.country_code)

        ctx.update({
            "rules_of_origin": rules_of_origin,
            "tariffs_and_charges_table_data": tariffs_and_charges_table_data,
            "quotas_table_data": quotas_table_data,
            "other_table_data": other_table_data,
            "column_titles": TABLE_COLUMN_TITLES,
            "regulation_groups": RegulationGroup.objects.inherited(commodity).order_by('title'),
            "modals": modals_dict,
            "is_eu_member": country.country_code.upper() == "EU",
        })

        tariff_content_context = get_tariff_content_context(country, commodity)
        ctx.update(tariff_content_context)

        return ctx


class CommodityDetailNorthernIrelandView(BaseCommodityDetailView):
    template_name = "commodities/commodity_detail_northern_ireland.html"


def measure_condition_detail(
    request, commodity_code, country_code, measure_id, nomenclature_sid
):
    """
    View for an individual measure condition detail page template which takes three arguments, the commodity code that
    the measure belongs to, the measure id of the individual measure being presented and the country code to
    provide the exporter geographical context
    :param nomenclature_sid:
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

    commodity = Commodity.objects.get(
        commodity_code=commodity_code, goods_nomenclature_sid=nomenclature_sid
    )
    import_measure = commodity.tts_obj.get_import_measure_by_id(
        int(measure_id), country_code=country_code
    )
    conditions = import_measure.get_measure_conditions_by_measure_id(int(measure_id))

    context = {
        "nomenclature_sid": nomenclature_sid,
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
    request, commodity_code, country_code, measure_id, order_number, nomenclature_sid
):
    """
    View for an individual measure condition detail page template which takes three arguments, the commodity code that
    the measure belongs to, the measure id of the individual measure being presented and the country code to
    provide the exporter geographical context
    :param nomenclature_sid:
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

    commodity = Commodity.objects.get(
        commodity_code=commodity_code, goods_nomenclature_sid=nomenclature_sid
    )
    import_measure = commodity.tts_obj.get_import_measure_by_id(
        int(measure_id), country_code=country_code
    )
    conditions = import_measure.get_measure_conditions_by_measure_id(int(measure_id))
    quota_def = import_measure.get_measure_quota_definition_by_order_number(
        order_number
    )
    geographical_area = import_measure.get_geographical_area()

    context = {
        "nomenclature_sid": nomenclature_sid,
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

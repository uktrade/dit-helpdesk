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

from flags.state import flag_enabled

from countries.models import Country

from hierarchy.views.sections import (
    BaseOtherMeasuresNorthernIrelandSection,
    BaseTariffsAndTaxesNorthernIrelandSection,
    OtherMeasuresSection,
    ProductRegulationsSection,
    ProductRegulationsNorthernIrelandSection,
    QuotasSection,
    QuotasNorthernIrelandSection,
    RulesOfOriginSection,
    RulesOfOriginNorthernIrelandSection,
    TariffsAndTaxesSection,
    TradeStatusSection,
    UKGTTariffsAndTaxesSection,
)
from hierarchy.views.base import (
    BaseSectionedCommodityObjectDetailView,
)

from .models import Commodity


class BaseSectionedCommodityDetailView(BaseSectionedCommodityObjectDetailView):
    def get_commodity_object(self, **kwargs):
        commodity_code = kwargs["commodity_code"]
        goods_nomenclature_sid = kwargs["nomenclature_sid"]

        return Commodity.objects.get(
            commodity_code=commodity_code,
            goods_nomenclature_sid=goods_nomenclature_sid,
        )

    def get_commodity_object_path(self, commodity):
        return commodity.get_path()

    def get_notes_context_data(self, commodity):
        ctx = {}

        heading = commodity.get_heading()
        chapter = heading.chapter
        section = chapter.section
        ctx["commodity_notes"] = commodity.tts_obj.footnotes
        ctx["chapter_notes"] = chapter.chapter_notes
        ctx["heading_notes"] = heading.heading_notes
        ctx["section_notes"] = section.section_notes

        return ctx


class CommodityDetailView(BaseSectionedCommodityDetailView):
    template_name = "commodities/commodity_detail.html"

    @property
    def sections(self):
        specific = [TariffsAndTaxesSection]

        if flag_enabled("PRE21"):
            specific = [
                TradeStatusSection,
                UKGTTariffsAndTaxesSection,
            ]

        common = [
            QuotasSection,
            OtherMeasuresSection,
            RulesOfOriginSection,
            ProductRegulationsSection,
        ]

        return specific + common


class CommodityEUCommodityObjectMixin:
    def get_eu_commodity_object(self, commodity_object):
        return Commodity.objects.for_region(
            settings.SECONDARY_REGION,
        ).get(
            commodity_code=commodity_object.commodity_code,
            goods_nomenclature_sid=commodity_object.goods_nomenclature_sid,
        )


class TariffsAndTaxesNorthernIrelandSection(CommodityEUCommodityObjectMixin, BaseTariffsAndTaxesNorthernIrelandSection):
    pass


class OtherMeasuresNorthernIrelandSection(CommodityEUCommodityObjectMixin, BaseOtherMeasuresNorthernIrelandSection):
    pass


class CommodityDetailNorthernIrelandView(BaseSectionedCommodityDetailView):
    sections = [
        TariffsAndTaxesNorthernIrelandSection,
        QuotasNorthernIrelandSection,
        OtherMeasuresNorthernIrelandSection,
        RulesOfOriginNorthernIrelandSection,
        ProductRegulationsNorthernIrelandSection,
    ]
    template_name = "commodities/commodity_detail_northern_ireland.html"

    def initialise(self, request, *args, **kwargs):
        super().initialise(request, *args, **kwargs)

        try:
            self.eu_commodity_object = Commodity.objects.for_region(
                settings.SECONDARY_REGION,
            ).get(
                commodity_code=self.commodity_object.commodity_code,
                goods_nomenclature_sid=self.commodity_object.goods_nomenclature_sid,
            )
        except Commodity.DoesNotExist:
            self.eu_commodity_object = None
        else:
            if self.eu_commodity_object.should_update_tts_content():
                self.eu_commodity_object.update_tts_content()


class MeasureConditionDetailView(TemplateView):
    template_name = "commodities/measure_condition_detail.html"

    def get(self, request, **kwargs):
        country_code = kwargs["country_code"]
        try:
            country = Country.objects.get(country_code=country_code.upper())
        except Country.DoesNotExist:
            messages.error(request, "Invalid originCountry")
            return redirect(reverse("choose-country"))
        self.country = country

        commodity_code = kwargs["commodity_code"]
        nomenclature_sid = kwargs["nomenclature_sid"]
        try:
            commodity = Commodity.objects.get(
                commodity_code=commodity_code,
                goods_nomenclature_sid=nomenclature_sid,
            )
        except Commodity.DoesNotExist:
            raise Http404
        if commodity.should_update_tts_content():
            commodity.update_tts_content()
        self.commodity = commodity

        measure_id = int(kwargs["measure_id"])
        self.import_measure = self.commodity.tts_obj.get_import_measure_by_id(
            measure_id,
            country_code=country_code
        )
        self.conditions = self.import_measure.get_measure_conditions_by_measure_id(
            measure_id,
        )

        return super().get(request, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        country = self.country
        commodity = self.commodity
        import_measure = self.import_measure
        conditions = self.conditions

        ctx.update({
            "nomenclature_sid": commodity.goods_nomenclature_sid,
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
        })

        return ctx


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
    if commodity.should_update_tts_content():
        commodity.update_tts_content()

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

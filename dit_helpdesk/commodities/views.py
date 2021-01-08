# -----------------------------------------------------------------------------
# NOTE - table column headers.
# -----------------------------------------------------------------------------
# If the table columns headings are changed, they also need to be updated in
# the SCSS file `_flexible-tables.scss` - otherwise the card-based layout for
# smaller screens will break.
# -----------------------------------------------------------------------------


from django.conf import settings

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
)
from hierarchy.views.base import (
    BaseMeasureConditionDetailView,
    BaseMeasureQuotaDetailView,
    BaseSectionedCommodityObjectDetailView,
)

from .models import Commodity


class CommodityObjectMixin:

    def get_commodity_object(self, **kwargs):
        commodity_code = kwargs["commodity_code"]
        nomenclature_sid = kwargs["nomenclature_sid"]

        return Commodity.objects.get(
            commodity_code=commodity_code,
            goods_nomenclature_sid=nomenclature_sid,
        )


class BaseSectionedCommodityDetailView(CommodityObjectMixin, BaseSectionedCommodityObjectDetailView):

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
    sections = [
        TradeStatusSection,
        TariffsAndTaxesSection,
        QuotasSection,
        OtherMeasuresSection,
        RulesOfOriginSection,
        ProductRegulationsSection,
    ]
    template_name = "commodities/commodity_detail.html"


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

        eu_commodity_object = Commodity.objects.for_region(
            settings.SECONDARY_REGION,
        ).get(
            commodity_code=self.commodity_object.commodity_code,
            goods_nomenclature_sid=self.commodity_object.goods_nomenclature_sid,
        )

        if eu_commodity_object.should_update_tts_content():
            eu_commodity_object.update_tts_content()


class MeasureConditionDetailView(CommodityObjectMixin, BaseMeasureConditionDetailView):
    pass


class MeasureQuotaDetailView(CommodityObjectMixin, BaseMeasureQuotaDetailView):
    pass


class EUCommodityObjectMixin:

    def get_commodity_object(self, **kwargs):
        commodity_code = kwargs["commodity_code"]
        nomenclature_sid = kwargs["nomenclature_sid"]

        return Commodity.objects.for_region(
            settings.SECONDARY_REGION,
        ).get(
            commodity_code=commodity_code,
            goods_nomenclature_sid=nomenclature_sid,
        )


class MeasureConditionDetailNorthernIrelandView(EUCommodityObjectMixin, BaseMeasureConditionDetailView):
    pass


class MeasureQuotaDetailNorthernIrelandView(EUCommodityObjectMixin, BaseMeasureQuotaDetailView):
    pass

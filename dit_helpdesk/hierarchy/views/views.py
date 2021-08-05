import logging

from django.conf import settings
from django.views.generic import TemplateView

from ..models import Chapter, Heading, SubHeading

from .base import (
    BaseCommodityObjectDetailView,
    BaseMeasureConditionDetailView,
    BaseMeasureQuotaDetailView,
    BaseSectionedCommodityObjectDetailView,
)
from .helpers import get_hierarchy_context_from_object
from ..helpers import get_code_argument_by_class
from .mixins import EUCommodityObjectMixin
from .sections import (
    HeadingOtherMeasuresNorthernIrelandSection,
    HeadingTariffsAndTaxesNorthernIrelandSection,
    ProductRegulationsSection,
    ProductRegulationsNorthernIrelandSection,
    QuotasSection,
    QuotasNorthernIrelandSection,
    OtherMeasuresSection,
    RulesOfOriginSection,
    RulesOfOriginNorthernIrelandSection,
    SubHeadingOtherMeasuresNorthernIrelandSection,
    SubHeadingTariffsAndTaxesNorthernIrelandSection,
    TariffsAndTaxesSection,
    TradeStatusSection,
)

from commodities.models import Commodity

logger = logging.getLogger(__name__)


class ChapterDetailView(BaseCommodityObjectDetailView):
    context_object_name = "chapter"
    model = Chapter
    template_name = "hierarchy/chapter_detail.html"

    def get_commodity_object_path(self, chapter):
        chapter_path = chapter.get_path()
        chapter_path.insert(0, [chapter])
        if chapter.get_hierarchy_children_count() > 0:
            chapter_path.insert(0, chapter.get_hierarchy_children())

        return chapter_path

    def get_notes_context_data(self, chapter):
        ctx = {}

        ctx["chapter_notes"] = chapter.chapter_notes
        ctx["section_notes"] = chapter.section.section_notes

        return ctx


class BaseSectionedHeadingDetailView(BaseSectionedCommodityObjectDetailView):
    context_object_name = "heading"
    model = Heading

    def get_commodity_object_path(self, heading):
        heading_path = heading.get_path()
        heading_path.insert(0, [heading])
        if heading.get_hierarchy_children_count() > 0:
            heading_path.insert(0, heading.get_hierarchy_children())

        return heading_path

    def get_notes_context_data(self, heading):
        ctx = {}

        chapter = heading.chapter
        section = chapter.section
        ctx["heading_notes"] = heading.heading_notes
        ctx["chapter_notes"] = chapter.chapter_notes
        ctx["section_notes"] = section.section_notes

        return ctx


class HeadingDetailView(BaseSectionedHeadingDetailView):
    sections = [
        TradeStatusSection,
        TariffsAndTaxesSection,
        QuotasSection,
        OtherMeasuresSection,
        RulesOfOriginSection,
        ProductRegulationsSection,
    ]
    template_name = "hierarchy/heading_detail.html"


class HeadingDetailNorthernIrelandView(BaseSectionedHeadingDetailView):
    sections = [
        HeadingTariffsAndTaxesNorthernIrelandSection,
        QuotasNorthernIrelandSection,
        HeadingOtherMeasuresNorthernIrelandSection,
        RulesOfOriginNorthernIrelandSection,
        ProductRegulationsNorthernIrelandSection,
    ]
    template_name = "hierarchy/heading_detail_northern_ireland.html"

    def initialise(self, request, *args, **kwargs):
        super().initialise(request, *args, **kwargs)

        eu_commodity_object = Heading.objects.for_region(
            settings.SECONDARY_REGION
        ).get_by_commodity_code(
            self.commodity_object.commodity_code,
            goods_nomenclature_sid=self.commodity_object.goods_nomenclature_sid,
        )

        if eu_commodity_object.should_update_tts_content():
            eu_commodity_object.update_tts_content()


class BaseSectionedSubHeadingDetailView(BaseSectionedCommodityObjectDetailView):
    context_object_name = "subheading"
    model = SubHeading

    def get_commodity_object_path(self, subheading):
        subheading_path = subheading.get_path()
        subheading_path.insert(0, [subheading])
        if subheading.get_hierarchy_children_count() > 0:
            subheading_path.insert(0, subheading.get_hierarchy_children())

        return subheading_path

    def get_notes_context_data(self, subheading):
        chapter = subheading.get_chapter()
        section = chapter.section

        return {
            "heading_notes": subheading.heading_notes,
            "chapter_notes": chapter.chapter_notes,
            "section_notes": section.section_notes,
        }


class SubHeadingDetailView(BaseSectionedSubHeadingDetailView):
    sections = [
        TradeStatusSection,
        TariffsAndTaxesSection,
        QuotasSection,
        OtherMeasuresSection,
        RulesOfOriginSection,
        ProductRegulationsSection,
    ]
    template_name = "hierarchy/subheading_detail.html"


class SubHeadingDetailNorthernIrelandView(BaseSectionedSubHeadingDetailView):
    sections = [
        SubHeadingTariffsAndTaxesNorthernIrelandSection,
        QuotasNorthernIrelandSection,
        SubHeadingOtherMeasuresNorthernIrelandSection,
        RulesOfOriginNorthernIrelandSection,
        ProductRegulationsNorthernIrelandSection,
    ]
    template_name = "hierarchy/subheading_detail_northern_ireland.html"

    def initialise(self, request, *args, **kwargs):
        super().initialise(request, *args, **kwargs)

        eu_commodity_object = SubHeading.objects.for_region(
            settings.SECONDARY_REGION
        ).get_by_commodity_code(
            commodity_code=self.commodity_object.commodity_code,
            goods_nomenclature_sid=self.commodity_object.goods_nomenclature_sid,
        )

        if eu_commodity_object.should_update_tts_content():
            eu_commodity_object.update_tts_content()


class MeasureConditionDetailView(BaseMeasureConditionDetailView):
    model = Heading


class MeasureQuotaDetailView(BaseMeasureQuotaDetailView):
    model = Heading


class MeasureConditionDetailNorthernIrelandView(
    EUCommodityObjectMixin, BaseMeasureConditionDetailView
):
    model = Heading


class MeasureQuotaDetailNorthernIrelandView(
    EUCommodityObjectMixin, BaseMeasureQuotaDetailView
):
    model = Heading


class MeasureSubHeadingConditionDetailView(BaseMeasureConditionDetailView):
    model = SubHeading


class MeasureSubHeadingQuotaDetailView(BaseMeasureQuotaDetailView):
    model = SubHeading


class MeasureSubHeadingConditionDetailNorthernIrelandView(
    EUCommodityObjectMixin, BaseMeasureConditionDetailView
):
    model = SubHeading


class MeasureSubHeadingQuotaDetailNorthernIrelandView(
    EUCommodityObjectMixin, BaseMeasureQuotaDetailView
):
    model = SubHeading


class HierarchyContextTreeView(TemplateView):

    template_name = "hierarchy/_hierarchy_modal.html"

    def get_context_data(self, *args, **kwargs):
        commodity_type = kwargs["commodity_type"]
        country_code = kwargs["country_code"]

        model = {
            "chapter": Chapter,
            "heading": Heading,
            "subheading": SubHeading,
            "commodity": Commodity,
        }[commodity_type]

        code, sid = kwargs["commodity_code"], kwargs["nomenclature_sid"]
        code_arg = get_code_argument_by_class(model)

        obj = model.objects.get(**{code_arg: code, "goods_nomenclature_sid": sid})

        hierarchy_tree_html = get_hierarchy_context_from_object(
            obj, country_code=country_code, links=False
        )

        commodity_code = obj.short_formatted_commodity_code

        return {"hierarchy_html": hierarchy_tree_html, "commodity_code": commodity_code}

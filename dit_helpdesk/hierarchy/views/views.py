import logging

from django.conf import settings
from django.contrib import messages
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect, render, reverse

from countries.models import Country
from regulations.models import RegulationGroup

from ..helpers import TABLE_COLUMN_TITLES
from ..models import Chapter, Heading, SubHeading

from .base import (
    BaseCommodityObjectDetailView,
    BaseMeasureConditionDetailView,
    BaseMeasureQuotaDetailView,
    BaseSectionedCommodityObjectDetailView,
)
from .helpers import (
    get_hierarchy_context,
    hierarchy_section_header,
    get_hierarchy_context_from_object,
)
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


def section_detail(request, section_id, country_code):
    """
    View for the heading detail page template which takes two arguments; the 10 digit code for the heading to
    display and the two character country code to provide the exporter geographical context which is
    used to display the appropriate related supporting content

    :param heading_code:
    :param request: django http request object
    :param country_code: string
    :return:
    """

    country = Country.objects.filter(country_code=country_code.upper()).first()

    if not country:
        messages.error(request, "Invalid originCountry")
        return redirect(reverse("choose-country"))

    section = get_object_or_404(Heading, heading_code=section_id)

    if section.should_update_tts_content():
        section.update_tts_content()

    import_measures = section.tts_obj.get_import_measures(country.country_code)

    table_data = [measure_json.get_table_row() for measure_json in import_measures]

    section_path = section.get_path()
    accordion_title = hierarchy_section_header(section_path)
    rules_of_origin = section.get_rules_of_origin(country_code=country.country_code)

    modals_dict = {}
    for measure_json in import_measures:
        modals_dict.update(measure_json.measures_modals)

    context = {
        "selected_origin_country": country.country_code,
        "section": section,
        "selected_origin_country_name": country.name,
        "rules_of_origin": rules_of_origin,
        "roo_footnotes": rules_of_origin,
        "table_data": table_data,
        "column_titles": TABLE_COLUMN_TITLES,
        "regulation_groups": RegulationGroup.objects.inherited(section).order_by(
            "title"
        ),
        "accordion_title": accordion_title,
        "section_hierarchy_context": get_hierarchy_context(
            section_path, country.country_code, section_id
        ),
        "modals": modals_dict,
    }

    return render(request, "hierarchy/section_detail.html", context)


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

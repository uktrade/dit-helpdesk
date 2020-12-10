import logging

from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.decorators import method_decorator

from core.helpers import require_feature
from countries.models import Country
from commodities.helpers import get_tariff_content_context
from regulations.models import RegulationGroup

from ..helpers import (
    get_nomenclature_group_measures,
    TABLE_COLUMN_TITLES,
)
from ..models import Chapter, Heading, SubHeading

from .base import (
    BaseCommodityObjectDetailView,
    BaseSectionedCommodityObjectDetailView,
)
from .helpers import (
    get_hierarchy_context,
    hierarchy_section_header,
)
from .sections import (
    HeadingTariffAndChargesNorthernIrelandSection,
    OtherMeasuresNorthernIrelandSection,
    ProductRegulationsNorthernIrelandSection,
    QuotasNorthernIrelandSection,
    RulesOfOriginNorthernIrelandSection,
    SubHeadingTariffAndChargesNorthernIrelandSection,
)

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
        "regulation_groups": RegulationGroup.objects.inherited(section).order_by('title'),
        "accordion_title": accordion_title,
        "section_hierarchy_context": get_hierarchy_context(
            section_path, country.country_code, section_id
        ),
        "modals": modals_dict,
    }

    return render(request, "hierarchy/section_detail.html", context)


def chapter_detail(request, chapter_code, country_code, nomenclature_sid):
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

    chapter = Chapter.objects.get(
        chapter_code=chapter_code, goods_nomenclature_sid=nomenclature_sid
    )
    if chapter.should_update_tts_content():
        chapter.update_tts_content()

    chapter_path = chapter.get_path()
    chapter_path.insert(0, [chapter])
    if chapter.get_hierarchy_children_count() > 0:
        chapter_path.insert(0, chapter.get_hierarchy_children())

    accordion_title = hierarchy_section_header(chapter_path)

    if chapter.should_update_tts_content():
        chapter.update_tts_content()

    context = {
        "selected_origin_country": country.country_code,
        "chapter": chapter,
        "selected_origin_country_name": country.name,
        "chapter_notes": chapter.chapter_notes,
        "section_notes": chapter.section.section_notes,
        "accordion_title": accordion_title,
        "chapter_hierarchy_context": get_hierarchy_context(
            chapter_path, country.country_code, chapter_code, chapter
        ),
    }

    return render(request, "hierarchy/chapter_detail.html", context)


class HeadingObjectMixin:
    context_object_name = "heading"

    def get_commodity_object(self, **kwargs):
        heading_code = kwargs["heading_code"]
        goods_nomenclature_sid = kwargs["nomenclature_sid"]

        return Heading.objects.get(
            heading_code=heading_code,
            goods_nomenclature_sid=goods_nomenclature_sid,
        )

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


class BaseHeadingDetailView(HeadingObjectMixin, BaseCommodityObjectDetailView):
    pass


class BaseSectionedHeadingDetailView(HeadingObjectMixin, BaseSectionedCommodityObjectDetailView):
    pass


class HeadingDetailView(BaseHeadingDetailView):

    def get_template_names(self):
        if settings.UKGT_ENABLED:
            template = "hierarchy/heading_detail_ukgt.html"
        else:
            template = "hierarchy/heading_detail.html"

        return [template]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        country = self.country
        heading = self.commodity_object

        import_measures = []
        tariffs_and_charges_table_data = []
        quotas_table_data = []
        other_table_data = []
        modals_dict = {}

        try:
            import_measures = heading.tts_obj.get_import_measures(country.country_code)

            tariffs_and_charges_measures = get_nomenclature_group_measures(
                heading, "Tariffs and charges", country.country_code
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
                heading, "Quotas", country.country_code
            )
            quotas_table_data = [
                measure_json.get_table_row() for measure_json in quotas_measures
            ]
            for measure_json in quotas_measures:
                modals_dict.update(measure_json.measures_modals)

            other_measures = get_nomenclature_group_measures(
                heading, "Other measures", country.country_code
            )
            other_table_data = [
                measure_json.get_table_row() for measure_json in other_measures
            ]
            for measure_json in other_measures:
                modals_dict.update(measure_json.measures_modals)

        except Exception as exc:
            logger.error("Heading detail error", exc_info=exc)

        rules_of_origin = heading.get_rules_of_origin(country_code=country.country_code)

        tariff_content_context = get_tariff_content_context(country, heading)
        ctx.update(tariff_content_context)

        if import_measures:
            ctx.update(
                {
                    "tariffs_and_charges_table_data": tariffs_and_charges_table_data,
                    "quotas_table_data": quotas_table_data,
                    "other_table_data": other_table_data,
                    "column_titles": TABLE_COLUMN_TITLES,
                    "modals": modals_dict,
                    "rules_of_origin": rules_of_origin,
                    "regulation_groups": RegulationGroup.objects.inherited(heading).order_by('title'),
                }
            )

        return ctx


@method_decorator(require_feature("NI_JOURNEY_ENABLED"), name="dispatch")
class HeadingDetailNorthernIrelandView(BaseSectionedHeadingDetailView):
    sections = [
        HeadingTariffAndChargesNorthernIrelandSection,
        QuotasNorthernIrelandSection,
        OtherMeasuresNorthernIrelandSection,
        RulesOfOriginNorthernIrelandSection,
        ProductRegulationsNorthernIrelandSection,
    ]
    template_name = "hierarchy/heading_detail_northern_ireland.html"

    def initialise(self, request, *args, **kwargs):
        super().initialise(request, *args, **kwargs)

        try:
            self.eu_commodity_object = Heading.objects.for_region(
                settings.SECONDARY_REGION,
            ).get(
                heading_code=self.commodity_object.heading_code,
                goods_nomenclature_sid=self.commodity_object.goods_nomenclature_sid,
            )
        except Heading.DoesNotExist:
            self.eu_commodity_object = None
        else:
            if self.eu_commodity_object.should_update_tts_content():
                self.eu_commodity_object.update_tts_content()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["column_titles"] = TABLE_COLUMN_TITLES

        return ctx


class SubHeadingObjectMixin:
    context_object_name = "subheading"

    def get_commodity_object(self, **kwargs):
        commodity_code = kwargs["commodity_code"]
        goods_nomenclature_sid = kwargs["nomenclature_sid"]

        return SubHeading.objects.get(
            commodity_code=commodity_code,
            goods_nomenclature_sid=goods_nomenclature_sid,
        )

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


class BaseSubHeadingDetailView(SubHeadingObjectMixin, BaseCommodityObjectDetailView):
    pass


class BaseSectionedSubHeadingDetailView(SubHeadingObjectMixin, BaseSectionedCommodityObjectDetailView):
    pass


class SubHeadingDetailView(BaseSubHeadingDetailView):

    def get_template_names(self):
        if settings.UKGT_ENABLED:
            template = "hierarchy/subheading_detail_ukgt.html"
        else:
            template = "hierarchy/subheading_detail.html"

        return [template]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        subheading = self.commodity_object
        country = self.country

        import_measures = []

        tariffs_and_charges_table_data = []
        quotas_table_data = []
        other_table_data = []

        modals_dict = {}
        try:
            import_measures = subheading.tts_obj.get_import_measures(country.country_code)

            tariffs_and_charges_measures = get_nomenclature_group_measures(
                subheading, "Tariffs and charges", country.country_code
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
                subheading, "Quotas", country.country_code
            )
            quotas_table_data = [
                measure_json.get_table_row() for measure_json in quotas_measures
            ]
            for measure_json in quotas_measures:
                modals_dict.update(measure_json.measures_modals)

            other_measures = get_nomenclature_group_measures(
                subheading, "Other measures", country.country_code
            )
            other_table_data = [
                measure_json.get_table_row() for measure_json in other_measures
            ]
            for measure_json in other_measures:
                modals_dict.update(measure_json.measures_modals)
        except Exception as exc:
            logger.error("Subheading detail error", exc_info=exc)

        rules_of_origin = subheading.get_rules_of_origin(country_code=country.country_code)

        tariff_content_context = get_tariff_content_context(country, subheading)
        ctx.update(tariff_content_context)

        if (
            import_measures
            and tariffs_and_charges_table_data
            or quotas_table_data
            or other_table_data
        ):
            ctx.update(
                {
                    "tariffs_and_charges_table_data": tariffs_and_charges_table_data,
                    "quotas_table_data": quotas_table_data,
                    "other_table_data": other_table_data,
                    "column_titles": TABLE_COLUMN_TITLES,
                    "modals": modals_dict,
                    "rules_of_origin": rules_of_origin,
                    "regulation_groups": RegulationGroup.objects.inherited(subheading).order_by('title'),
                }
            )

        return ctx


@method_decorator(require_feature("NI_JOURNEY_ENABLED"), name="dispatch")
class SubHeadingDetailNorthernIrelandView(BaseSectionedSubHeadingDetailView):
    sections = [
        SubHeadingTariffAndChargesNorthernIrelandSection,
        QuotasNorthernIrelandSection,
        OtherMeasuresNorthernIrelandSection,
        RulesOfOriginNorthernIrelandSection,
        ProductRegulationsNorthernIrelandSection,
    ]
    template_name = "hierarchy/subheading_detail_northern_ireland.html"

    def initialise(self, request, *args, **kwargs):
        super().initialise(request, *args, **kwargs)

        try:
            self.eu_commodity_object = SubHeading.objects.for_region(
                settings.SECONDARY_REGION,
            ).get(
                commodity_code=self.commodity_object.commodity_code,
                goods_nomenclature_sid=self.commodity_object.goods_nomenclature_sid,
            )
        except SubHeading.DoesNotExist:
            self.eu_commodity_object = None
        else:
            if self.eu_commodity_object.should_update_tts_content():
                self.eu_commodity_object.update_tts_content()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["column_titles"] = TABLE_COLUMN_TITLES

        return ctx


def measure_condition_detail(
    request, heading_code, country_code, measure_id, nomenclature_sid
):
    """
    View for an individual measure condition detail page template which takes three arguments, the commodity code that
    the measure belongs to, the measure id of the individual measure being presented and the country code to
    provide the exporter geographical context
    :param heading_code:
    :param request: django http request object
    :param country_code: string
    :param measure_id: int
    :return:
    """

    country = Country.objects.filter(country_code=country_code.upper()).first()

    if not country:
        messages.error(request, "Invalid originCountry")
        return redirect(reverse("choose-country"))

    heading = Heading.objects.get(
        heading_code=heading_code,
        goods_nomenclature_sid=nomenclature_sid,
    )
    if heading.should_update_tts_content():
        heading.update_tts_content()

    import_measure = heading.tts_obj.get_import_measure_by_id(
        int(measure_id), country_code=country_code
    )
    conditions = import_measure.get_measure_conditions_by_measure_id(int(measure_id))

    context = {
        "selected_origin_country": country.country_code,
        "heading": heading,
        "commodity_code_split": heading.heading_code_split,
        "selected_origin_country_name": country.name,
        "import_measure": import_measure,
        "conditions": conditions,
    }

    return render(request, "hierarchy/measure_condition_detail.html", context)


def measure_quota_detail(
    request, heading_code, country_code, measure_id, order_number, nomenclature_sid
):
    """
    View for an individual measure condition detail page template which takes three arguments, the commodity code that
    the measure belongs to, the measure id of the individual measure being presented and the country code to
    provide the exporter geographical context
    :param heading_code:
    :param request: django http request object
    :param country_code: string
    :param measure_id: int
    :return:
    """

    country = Country.objects.filter(country_code=country_code.upper()).first()

    if not country:
        messages.error(request, "Invalid originCountry")
        return redirect(reverse("choose-country"))

    heading = Heading.objects.get(
        heading_code=heading_code,
        goods_nomenclature_sid=nomenclature_sid,
    )
    if heading.should_update_tts_content():
        heading.update_tts_content()

    import_measure = heading.tts_obj.get_import_measure_by_id(
        int(measure_id), country_code=country_code
    )
    quota_def = import_measure.get_measure_quota_definition_by_order_number(
        order_number
    )
    geographical_area = import_measure.get_geographical_area()

    context = {
        "selected_origin_country": country.country_code,
        "commodity_description": heading.description,
        "commodity_code": heading.commodity_code,
        "selected_origin_country_name": country.name,
        "quota_def": quota_def,
        "geographical_area": geographical_area,
        "commodity_code_split": heading.heading_code_split,
        "measure_type": import_measure.type_description,
    }

    return render(request, "hierarchy/measure_quota_detail.html", context)

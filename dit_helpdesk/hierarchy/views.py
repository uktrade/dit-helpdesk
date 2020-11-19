import logging
import re

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from commodities.models import Commodity
from commodities.helpers import (
    get_global_tariff_context,
    get_tariff_content_context,
)
from core.helpers import require_feature
from countries.models import Country
from regulations.models import RegulationGroup

from .helpers import (
    get_eu_commodity_link,
    get_nomenclature_group_measures,
    TABLE_COLUMN_TITLES,
)
from .models import Section, Chapter, Heading, SubHeading

code_regex = re.compile("([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})")

logger = logging.getLogger(__name__)


def _get_expanded_context(selected_node_id):
    """
    Given a selected_node_id (a location in the hierarchy), return
    a list of hierarchy ids that make up the path to the currently expanded context.
    """
    if selected_node_id == "root":
        return []

    expanded = []
    node_type, node_pk = selected_node_id.split("-")

    if node_type == "section":
        expanded.append(selected_node_id)

    elif node_type == "chapter":
        chapter_obj = Chapter.objects.get(goods_nomenclature_sid=node_pk)
        expanded.append("section-{0}".format(chapter_obj.section.section_id))
        expanded.append("chapter-{0}".format(node_pk))

    elif node_type == "heading":
        heading_obj = Heading.objects.get(goods_nomenclature_sid=node_pk)

        expanded.append("section-{0}".format(heading_obj.chapter.section.section_id))
        expanded.append(
            "chapter-{0}".format(heading_obj.chapter.goods_nomenclature_sid)
        )
        expanded.append("heading-{0}".format(heading_obj.goods_nomenclature_sid))

    elif node_type == "sub_heading":

        current = SubHeading.objects.get(goods_nomenclature_sid=node_pk)
        while True:
            expanded.append("sub_heading-{0}".format(current.goods_nomenclature_sid))
            current = current.get_parent()
            if type(current) is Heading:
                break
        heading_obj = current

        expanded.append("section-{0}".format(heading_obj.chapter.section.section_id))
        expanded.append(
            "chapter-{0}".format(heading_obj.chapter.goods_nomenclature_sid)
        )
        expanded.append("heading-{0}".format(heading_obj.goods_nomenclature_sid))

    return expanded


def _get_hierarchy_level_html(node, expanded, origin_country):
    """
    View helper function to return the html for the selected hierarchy node
    :param node: string or model instance the current node
    :param expanded: list of hierarchy ids that make up the currently expanded path
    :param origin_country: string representing the origin country code
    :return: html snippet that represents the expanded section of the hierarchy
    """
    if node == "root":  # if root it list only sections
        children = (
            Section.objects.all().order_by("section_id").prefetch_related("chapter_set")
        )
        html = '<ul class="app-hierarchy-tree">'
        end = "\n</ul>"
    else:
        children = node.get_hierarchy_children()
        html = '\n<ul class="app-hierarchy-tree--child">'
        end = "\n</ul>\n</li>"

    for child in children:
        if child.hierarchy_key in expanded:
            openclass = "open"
        else:
            openclass = "closed"

        if type(child) is Section:
            li = f'<li id="{child.hierarchy_key}" class="app-hierarchy-tree__part app-hierarchy-tree__section app-hierarchy-tree__parent--{openclass}"><a href="{child.get_hierarchy_url(origin_country)}" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">{child.title.capitalize()}</a> <span class="app-hierarchy-tree__section-numbers">Section {child.roman_numeral}</span> <span class="app-hierarchy-tree__chapter-range">{child.chapter_range_str}</span>'
        elif type(child) in [Commodity, Heading, SubHeading] and (
            type(child) is Commodity or child.get_hierarchy_children_count() == 0
        ):
            li = f'<li id="{child.hierarchy_key}" class="app-hierarchy-tree__part app-hierarchy-tree__commodity"><div class="app-hierarchy-tree__link"><a href="{child.get_absolute_url(origin_country)}" class="app-hierarchy-tree__link--child">{child.description}<span class="govuk-visually-hidden"> &ndash; </span></a></div>{_commodity_code_html(child)}</li>'
        else:
            li = f'<li id="{child.hierarchy_key}" class="app-hierarchy-tree__part app-hierarchy-tree__chapter app-hierarchy-tree__parent--{openclass}"><a href="{child.get_hierarchy_url(origin_country)}" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">{child.description.capitalize()}</a>{_commodity_code_html(child)}'
        html = html + li

        if child.hierarchy_key in expanded:
            html = html + _get_hierarchy_level_html(child, expanded, origin_country)

    html = html + end

    return html


def _get_hierarchy_level_json(node, expanded, origin_country):
    """
    View helper function to return the JSON for the selected hierarchy node
    :param node: string or model instance the current node
    :param expanded: list of hierarchy ids that make up the currently expanded path
    :param origin_country: string representing the origin country code
    :return: dict that represents the expanded section of the hierarchy
    """

    serialized = []

    if node == "root":  # if root it list only sections
        children = (
            Section.objects.all().order_by("section_id").prefetch_related("chapter_set")
        )
    else:
        children = node.get_hierarchy_children()

    for child in children:
        element = {"key": child.hierarchy_key}
        if type(child) is Section:
            element.update(
                {
                    "type": "branch",
                    "roman_numeral": child.roman_numeral,
                    "chapter_range_str": child.chapter_range_str,
                    "label": child.title,
                }
            )
        else:
            if type(child) is Commodity or child.get_hierarchy_children_count() == 0:
                element["type"] = "leaf"
            else:
                element["type"] = "parent"
            code = (
                child.commodity_code
                if isinstance(child, Commodity)
                else child.harmonized_code
            )
            element["commodity_code"] = code_regex.search(code).groups()
            element["label"] = child.description

        if child.hierarchy_key in expanded:
            element["children"] = _get_hierarchy_level_json(
                node=child, expanded=expanded, origin_country=origin_country
            )

        serialized.append(element)
    return serialized


def hierarchy_data(country_code, node_id="root", content_type="html"):
    """
    View helper function
    :param country_code: string representing country code
    :param node_id: string representing hierarchy node id
    :return: html snippet that represents the expanded section of the hierarchy
    """
    node_id = node_id.rstrip("/")
    expanded = _get_expanded_context(node_id)
    serializers = {"html": _get_hierarchy_level_html, "json": _get_hierarchy_level_json}
    serializer = serializers[content_type]
    return serializer(node="root", expanded=expanded, origin_country=country_code)


class Redirect(Exception):

    def __init__(self, redirect_to, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.redirect_to = redirect_to


class BaseCommodityObjectDetailView(TemplateView):
    context_object_name = None

    def get_commodity_object(self, **kwargs):
        raise NotImplementedError("Implement `get_commodity_object`")

    def initialise(self, request, *args, **kwargs):
        country_code = kwargs["country_code"]
        try:
            self.country = Country.objects.get(country_code=country_code.upper())
        except Country.DoesNotExist:
            messages.error(request, "Invalid originCountry")
            raise Redirect(redirect("choose-country"))

        try:
            self.commodity_object = self.get_commodity_object(**kwargs)
        except ObjectDoesNotExist:
            raise Http404

        if self.commodity_object.should_update_content():
            self.commodity_object.update_content()

    def get(self, request, *args, **kwargs):
        try:
            self.initialise(request, *args, **kwargs)
        except Redirect as r:
            messages.error(request, "Invalid originCountry")
            return r.redirect_to

        return super().get(request, *args, **kwargs)

    def get_commodity_object_path(self, commodity_object):
        raise NotImplementedError("Implement `get_commodity_object_path`")

    def get_hierarchy_section_header(self, path):
        """
        View helper function to extract the Section Numeral and title for the hierarchy context of the commodity
        and returned as formatted html string
        :param reversed_commodity_tree: list
        :return: html
        """
        section_index = len(path) - 1
        section = path[section_index][0]
        html = f"Section {section.roman_numeral}: {section.title.capitalize()}"

        return html

    def get_hierarchy_context(self, commodity_path, country_code, commodity_code, current_item):
        return get_hierarchy_context(commodity_path, country_code, commodity_code, current_item)

    def get_notes_context_data(self, commodity_object):
        raise NotImplementedError("Implement `get_notes_context_data`")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        commodity_object = self.commodity_object
        country = self.country

        ctx["selected_origin_country"] = country.country_code
        ctx["selected_origin_country_name"] = country.name

        commodity_object_path = self.get_commodity_object_path(self.commodity_object)
        ctx["accordion_title"] = self.get_hierarchy_section_header(commodity_object_path)
        ctx["hierarchy_context"] = self.get_hierarchy_context(
            commodity_object_path,
            country.country_code,
            commodity_object.commodity_code,
            commodity_object,
        )

        ctx["commodity"] = commodity_object
        if self.context_object_name:
            ctx[self.context_object_name] = commodity_object

        ctx["is_eu_member"] = country.country_code.upper() == "EU"

        ctx.update(self.get_notes_context_data(self.commodity_object))

        return ctx


class BaseSectionedCommodityObjectDetailView(BaseCommodityObjectDetailView):

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        sections = []
        section_menu_items = []
        modals = {}
        for section_class in self.sections:
            section = section_class(self.country, self.commodity_object)
            if not section.should_be_displayed:
                continue

            ctx.update(section.get_context_data())
            sections.append(section)

            section_menu_items += section.get_menu_items()

            for modals_context_data in section.get_modals_context_data():
                modals.update(modals_context_data)

        ctx["sections"] = sections
        ctx["section_menu_items"] = section_menu_items
        ctx["modals"] = modals

        return ctx


class CommodityDetailSection:
    should_be_displayed = True

    def __init__(self, country, commodity_object):
        self.country = country
        self.commodity_object = commodity_object

    def get_menu_items(self):
        raise NotImplementedError("Implement `get_menu_items`")

    def get_modals_context_data(self):
        return []

    def get_context_data(self):
        raise NotImplementedError("Implement `get_context_data`")


class BaseTariffAndChargesNorthernIrelandSection(CommodityDetailSection):
    template = "hierarchy/_tariffs_and_charges_northern_ireland.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        self.uk_tariffs_and_charges_measures = get_nomenclature_group_measures(
            self.commodity_object,
            "Tariffs and charges",
            self.country.country_code,
        )

        eu_commodity_object = self.get_eu_commodity_object(commodity_object)
        self.eu_tariffs_and_charges_measures = get_nomenclature_group_measures(
            eu_commodity_object,
            "Tariffs and charges",
            self.country.country_code,
        )

    def get_eu_commodity_object(self, commodity_object):
        raise NotImplementedError("Implement `get_eu_commodity_object`")

    @property
    def should_be_displayed(self):
        return bool(self.uk_tariffs_and_charges_measures)

    def get_menu_items(self):
        return [
            ("Tariffs and charges", "tariffs_and_charges"),
        ]

    def get_modals_context_data(self):
        return [
            measure_json.measures_modals
            for measure_json in self.uk_tariffs_and_charges_measures
        ]

    def _get_table_data(self, charges_and_measures):
        is_eu = self.country.country_code.upper() == "EU"

        tariffs_and_charges_table_data = (
            [
                measure_json.get_table_row()
                for measure_json in charges_and_measures
                if measure_json.vat or measure_json.excise
            ]
            if is_eu
            else
            [
                measure_json.get_table_row()
                for measure_json in charges_and_measures
            ]
        )

        return tariffs_and_charges_table_data

    def get_context_data(self):
        ctx = {
            "uk_tariffs_and_charges_table_data": self._get_table_data(self.uk_tariffs_and_charges_measures),
            "eu_tariffs_and_charges_table_data": self._get_table_data(self.eu_tariffs_and_charges_measures),
        }

        if settings.UKGT_ENABLED:
            ctx["global_tariff_data"] = get_global_tariff_context(self.commodity_object)

        return ctx


class QuotasNorthernIrelandSection(CommodityDetailSection):
    template = "hierarchy/_quotas_northern_ireland.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        self.has_quotas_measures = True

        self.quotas_measures = get_nomenclature_group_measures(
            self.commodity_object,
            "Quotas",
            self.country.country_code,
        )

        try:
            self.quotas_table_data = self._get_table_data(self.quotas_measures)
        except Exception as ex:
            self.has_quotas_measures = False
            logger.info(ex.args)

    @property
    def should_be_displayed(self):
        return self.has_quotas_measures and bool(self.quotas_measures)

    def get_menu_items(self):
        return [
            ("Quotas", "quotas"),
        ]

    def get_modals_context_data(self):
        return [
            measure_json.measures_modals
            for measure_json in self.quotas_measures
        ]

    def _get_table_data(self, quotas_measures):
        return [
            measure_json.get_table_row() for measure_json in quotas_measures
        ]

    def get_context_data(self):
        return {
            "eu_quotas_link": get_eu_commodity_link(self.commodity_object, self.country),
            "quotas_table_data": self.quotas_table_data,
        }


class OtherMeasuresNorthernIrelandSection(CommodityDetailSection):
    template = "hierarchy/_other_measures_northern_ireland.html"

    def __init__(self, country, commodity_object):
        super().__init__(country, commodity_object)

        self.has_other_measures = True

        self.other_measures = get_nomenclature_group_measures(
            commodity_object,
            "Other measures",
            country.country_code,
        )

        try:
            self.other_measures_table_data = [measure_json.get_table_row() for measure_json in self.other_measures]
        except Exception as ex:
            self.has_other_measures = False
            logger.info(ex.args)

    @property
    def should_be_displayed(self):
        return self.has_other_measures and bool(self.other_measures)

    def get_menu_items(self):
        return [("Other measures", "other_measures")]

    def get_modals_context_data(self):
        return [
            measure_json.measures_modals
            for measure_json in self.other_measures
        ]

    def get_context_data(self):
        return {
            "eu_other_measures_link": get_eu_commodity_link(self.commodity_object, self.country),
            "other_measures_table": self.other_measures_table_data,
        }


class RulesOfOriginNorthernIrelandSection(CommodityDetailSection):
    template = "hierarchy/_rules_of_origin_northern_ireland.html"

    def get_menu_items(self):
        return [("Rules of origin", "rules_of_origin")]

    def get_context_data(self):
        commodity_object = self.commodity_object
        country = self.country

        rules_of_origin = commodity_object.get_rules_of_origin(
            country_code=country.country_code,
        )

        return {
            "eu_rules_of_origin_link": get_eu_commodity_link(commodity_object, country),
            "rules_of_origin": rules_of_origin,
        }


class ProductRegulationsNorthernIrelandSection(CommodityDetailSection):
    template = "hierarchy/_product_regulations_northern_ireland.html"

    def get_menu_items(self):
        return [("Product-specific regulations", "regulations")]

    def get_context_data(self):
        return {
            "eu_regulations_link": get_eu_commodity_link(self.commodity_object, self.country),
        }


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

    if section.should_update_content():
        section.update_content()

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

    chapter_path = chapter.get_path()
    chapter_path.insert(0, [chapter])
    if chapter.get_hierarchy_children_count() > 0:
        chapter_path.insert(0, chapter.get_hierarchy_children())

    accordion_title = hierarchy_section_header(chapter_path)

    try:
        if chapter.should_update_content():
            chapter.update_content()

    except Exception as ex:
        logger.info("chapter notes: ", ex.args)

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

        except Exception as ex:
            logger.info(ex.args)

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


class HeadingTariffAndChargesNorthernIrelandSection(BaseTariffAndChargesNorthernIrelandSection):

    def get_eu_commodity_object(self, commodity_object):
        return Heading.objects.for_region(
            settings.SECONDARY_REGION,
        ).get(
            heading_code=commodity_object.heading_code,
            goods_nomenclature_sid=commodity_object.goods_nomenclature_sid,
        )


@method_decorator(require_feature("NI_JOURNEY_ENABLED"), name="dispatch")
class HeadingDetailNorthernIrelandView(BaseSectionedHeadingDetailView):
    sections = [
        HeadingTariffAndChargesNorthernIrelandSection,
        QuotasNorthernIrelandSection,
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
            if self.eu_commodity_object.should_update_content():
                self.eu_commodity_object.update_content()

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

        except Exception as ex:
            logger.info("subheading 2: ", ex.args)

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


class SubHeadingTariffAndChargesNorthernIrelandSection(BaseTariffAndChargesNorthernIrelandSection):

    def get_eu_commodity_object(self, commodity_object):
        return SubHeading.objects.for_region(
            settings.SECONDARY_REGION,
        ).get(
            commodity_code=commodity_object.commodity_code,
            goods_nomenclature_sid=commodity_object.goods_nomenclature_sid,
        )


@method_decorator(require_feature("NI_JOURNEY_ENABLED"), name="dispatch")
class SubHeadingDetailNorthernIrelandView(BaseSectionedSubHeadingDetailView):
    sections = [
        SubHeadingTariffAndChargesNorthernIrelandSection,
        QuotasNorthernIrelandSection,
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
            if self.eu_commodity_object.should_update_content():
                self.eu_commodity_object.update_content()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["column_titles"] = TABLE_COLUMN_TITLES

        return ctx


def hierarchy_section_header(reversed_heading_tree):
    """
    View helper function to extract the Section Numeral and title for the hierarchy context of the heading
    and returned as formatted html string
    :param reversed_heading_tree:
    :return: html
    """
    section_index = len(reversed_heading_tree) - 1
    section = reversed_heading_tree[section_index][0]
    html = f"Section {section.roman_numeral}: {section.title.capitalize()}"
    return html


def get_hierarchy_item_by_code(code):

    try:
        return Chapter.objects.get(chapter_code=code)
    except ObjectDoesNotExist:
        pass

    try:
        return Heading.objects.get(heading_code=code)
    except ObjectDoesNotExist:
        pass

    try:
        subheading = SubHeading.objects.filter(commodity_code=code)
        if type(subheading) == SubHeading:
            return subheading
        elif len(subheading) > 0:
            return subheading.first()
        else:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        pass

    try:
        return Commodity.objects.get(commodity_code=code)
    except ObjectDoesNotExist:
        pass


def _commodity_code_html(item, ignore_duplicate=True):
    """
    View helper function that genrates an html representation of the ten digit commodity code broken into three groups
    of 6, 2 and  digits and colour code formatted
    :param item: model instance
    :return: html
    """

    if ignore_duplicate:
        if isinstance(item, SubHeading) and item.is_duplicate_heading():
            return '<span class="app-commodity-code app-hierarchy-tree__commodity-code">&nbsp;</span>'

        if isinstance(item, Heading) and item.is_duplicate_heading():
            return '<span class="app-commodity-code app-hierarchy-tree__commodity-code">&nbsp;</span>'

    leaf = False

    if isinstance(item, str):
        code = item
    elif isinstance(item, Chapter):
        code = item.chapter_code
    elif isinstance(item, Heading):
        code = item.heading_code
    else:
        code = item.commodity_code

    if (
        type(item) == Commodity
        or hasattr(item, "get_hierarchy_children_count")
        and item.get_hierarchy_children_count() == 0
    ):
        leaf = True

    commodity_code_html = (
        '<span class="app-commodity-code app-hierarchy-tree__commodity-code">'
    )

    if len(code) > 2 and code.isdigit():

        code_regex = re.search(
            "([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})([0-9]{2})", code
        )

        code_split = [
            code_regex.group(1),
            code_regex.group(2),
            code_regex.group(3),
            code_regex.group(4),
            code_regex.group(5),
        ]

        blank_span_html = ['<span class="app-commodity-code__is-blank">', "</span>"]

        for index, code_segment in enumerate(code_split):
            counter = str(int(index) + 1)
            if code[2:] == "00000000" and int(counter) > 1:
                blank_span = blank_span_html if not leaf else ["", ""]
            elif code[4:] == "000000" and int(counter) > 2:
                blank_span = blank_span_html if not leaf else ["", ""]
            elif code[6:] == "0000" and int(counter) > 3:
                blank_span = blank_span_html if not leaf else ["", ""]
            elif code[8:] == "00" and int(counter) > 4:
                blank_span = blank_span_html if not leaf else ["", ""]
            else:
                blank_span = ["", ""]

            commodity_code_html += '<span class="app-commodity-code__highlight app-commodity-code__highlight--{0}">{1}{2}{3}</span>'.format(
                counter, blank_span[0], code_segment, blank_span[1]
            )

    else:
        commodity_code_html + code

    commodity_code_html = commodity_code_html + "</span>"

    return commodity_code_html


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
        heading_code=heading_code, goods_nomenclature_sid=nomenclature_sid
    )
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
        heading_code=heading_code, goods_nomenclature_sid=nomenclature_sid
    )
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


def get_hierarchy_context(commodity_path, country_code, commodity_code, current_item):
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
    html = ""
    reversedList = reversed(commodity_path)

    for index, lista in enumerate(reversedList):
        if index == 0:
            # We dont want to retrieve section as it is explicity renders by commodity_hierarchy_section_header
            html += "<nav>"
        else:
            html += f"<ul>"
            for i, item in enumerate(lista):
                commodity_type = ""
                if type(item) is Chapter:
                    item_commodity_code = item.chapter_code
                    commodity_type = "chapter"
                    nomenclature_sid = item.goods_nomenclature_sid
                elif type(item) is Heading:
                    item_commodity_code = item.heading_code
                    commodity_type = "heading"
                    nomenclature_sid = item.goods_nomenclature_sid
                elif type(item) is SubHeading:
                    item_commodity_code = item.commodity_code
                    commodity_type = "subheading"
                    nomenclature_sid = item.goods_nomenclature_sid
                else:
                    item_commodity_code = item.commodity_code
                    commodity_type = "commodity"
                    nomenclature_sid = item.goods_nomenclature_sid

                if item_commodity_code == commodity_code and item == current_item:
                    html += f"""<li><div class="govuk-body govuk-!-font-weight-bold app-hierarchy-tree__link govuk-!-font-size-16">{item.description.capitalize()}</div><div class="govuk-visually-hidden"> &ndash; </div><strong>{_commodity_code_html(item)}</strong></li>"""
                else:

                    if commodity_type == "chapter":

                        nomenclature_link = reverse(
                            "chapter-detail",
                            kwargs={
                                "country_code": country_code,
                                "chapter_code": item_commodity_code,
                                "nomenclature_sid": nomenclature_sid,
                            },
                        )

                    elif commodity_type == "heading":

                        nomenclature_link = reverse(
                            "heading-detail",
                            kwargs={
                                "country_code": country_code,
                                "heading_code": item_commodity_code,
                                "nomenclature_sid": nomenclature_sid,
                            },
                        )

                    elif commodity_type == "subheading":

                        nomenclature_link = reverse(
                            "subheading-detail",
                            kwargs={
                                "country_code": country_code,
                                "commodity_code": item_commodity_code,
                                "nomenclature_sid": nomenclature_sid,
                            },
                        )

                    else:

                        nomenclature_link = reverse(
                            "commodity-detail",
                            kwargs={
                                "country_code": country_code,
                                "commodity_code": item_commodity_code,
                                "nomenclature_sid": nomenclature_sid,
                            },
                        )

                    html += f"""<li><a href="{nomenclature_link}" class="app-hierarchy-tree__link app-hierarchy-tree__link--parent">{item.description.capitalize()}</a>{_commodity_code_html(item)}"""

                if index is listSize:
                    html += "</li>"

            if index is listSize:
                for i in range(0, listSize):
                    # close
                    html += "</ul></nav>"

    return html

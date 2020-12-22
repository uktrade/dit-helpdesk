from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView

from countries.models import Country

from ..helpers import get_eu_commodity_link, TABLE_COLUMN_TITLES

from .exceptions import Redirect
from .helpers import get_hierarchy_context


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

        if self.commodity_object.should_update_tts_content():
            self.commodity_object.update_tts_content()

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
        ctx["eu_regulations_link"] = get_eu_commodity_link(commodity_object, country)

        ctx.update(self.get_notes_context_data(self.commodity_object))

        ctx["column_titles"] = TABLE_COLUMN_TITLES

        return ctx


class BaseSectionedCommodityObjectDetailView(BaseCommodityObjectDetailView):

    @property
    def sections(self):
        raise NotImplementedError("Add property `sections` as a list of `CommodityDetailSection` classes")

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

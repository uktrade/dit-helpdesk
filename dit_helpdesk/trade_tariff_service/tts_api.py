import logging
import re
import requests

from datetime import datetime

from django.db import connection
from django.template import loader
from dateutil.parser import parse as parse_dt
from django.conf import settings

from countries.models import Country

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


COMMODITY_DETAIL_TABLE_KEYS = [
    ("country", "Country"),
    ("measure_description", "Measure type"),
    ("measure_value", "Value"),
    ("conditions_html", "Conditions"),
    # ("excluded_countries", "Excluded countries"),
    ("start_end_date", "Start date"),
]


class BaseCommodityJson:
    def __init__(self, commodity_obj, di):
        self.commodity_obj = commodity_obj
        self.di = di

    @property
    def title(self):
        return self.di["formatted_description"].replace("&nbsp;", " ").strip()

    @property
    def code(self):
        return self.di["goods_nomenclature_item_id"]

    @property
    def footnotes(self):
        if "footnotes" not in self.di:
            return []

        return self.di["footnotes"]

    @property
    def is_meursing_code(self):
        return self.di.get("meursing_code", False)

    def get_import_measures(self, origin_country, vat=None, excise=None):
        if "import_measures" not in self.di:
            return []

        measures = [
            ImportMeasureJson(self.commodity_obj, d, self.code, self.title, origin_country)
            for d in self.di["import_measures"]
        ]

        measures = [
            json_obj
            for json_obj in measures
            if json_obj.is_relevant_for_origin_country(origin_country)
        ]

        if vat is not None:
            measures = [obj for obj in measures if obj.vat == vat]
        if excise is not None:
            measures = [obj for obj in measures if obj.excise == excise]

        return measures

    def get_import_measure_by_id(self, measure_id, country_code=None):
        measures = [
            measure
            for measure in self.get_import_measures(country_code)
            if measure.measure_id == measure_id
        ]

        return measures[0] if len(measures) == 1 else None


class CommodityJson(BaseCommodityJson):

    def __repr__(self):
        return "CommodityJson"

    @property
    def title(self):
        return self.di["description"]

    @property
    def chapter_note(self):
        return self.di["chapter"]["chapter_note"]


class ChapterJson(BaseCommodityJson):

    @property
    def chapter_note(self):
        if self.di and "chapter_note" in self.di.keys():
            return self.di["chapter_note"]
        return ""


class HeadingJson(BaseCommodityJson):
    pass


class SubHeadingJson(BaseCommodityJson):
    pass


class ImportMeasureJson:
    def __init__(self, commodity_obj, di, commodity_code, commodity_title, country_code):
        self.commodity_obj = commodity_obj
        self.di = di
        self.commodity_code = commodity_code
        self.commodity_title = commodity_title
        self.measures_modals = {}
        self.country_code = country_code

    def __repr__(self):
        return "ImportMeasureJson %s %s" % (self.commodity_code, self.type_id)

    @property
    def origin(self):
        return self.di["origin"]  # e.g. "uk"

    @property
    def type_id(self):
        """
        returns type_id

        e.g. "VTZ", "VTS", "103" (103 is third world duty)
        (142, tariff preference, e.g. preferential rate for particular countries;
        122-125 quota limit)

        """
        return self.di["measure_type"]["id"]

    @property
    def type_description(self):
        # NOTE: localised measure type descriptions are in the dumped database
        return self.di["measure_type"]["description"]

    @property
    def measure_id(self):
        return self.di["measure_id"]

    @property
    def excluded_country_area_ids(self):
        return [di["geographical_area_id"] for di in self.di["excluded_countries"]]

    @property
    def vat(self):
        return self.di["vat"]

    @property
    def excise(self):
        return self.di["excise"]

    @property
    def num_conditions(self):
        return len(self.di["measure_conditions"])

    @property
    def geographical_area_description(self):
        geographical_area_description = self.di["geographical_area"]["description"]
        if self.di["geographical_area"]["id"][0].isalpha():
            geographical_area_description = geographical_area_description + " (%s)" % self.di["geographical_area"]["id"]

        return geographical_area_description

    @property
    def is_gsp(self):
        return self.geographical_area_description.startswith("GSP")

    def is_relevant_for_origin_country(self, origin_country_code):
        geo_area = self.di["geographical_area"]
        if geo_area is None:
            return False

        def does_area_id_match(area):
            if not area["id"][0].isalpha():
                return False
            return area["id"] == origin_country_code.upper()

        if does_area_id_match(geo_area):
            return True

        for child_area in geo_area["children_geographical_areas"]:
            if does_area_id_match(child_area):
                return True

        return False

    @property
    def conditions_html(self):
        if not self.num_conditions:
            html = "-"
        else:
            url = self.commodity_obj.get_conditions_url(
                self.country_code.lower(),
                self.measure_id,
            )
            modal_id = "{0}-{1}".format(self.commodity_code, self.measure_id)
            html = """<a data-toggle="modal" data-target="{0}" href="{1}">Conditions</a>""".format(
                modal_id, url
            )
            self.measures_modals[modal_id] = self.get_modal(
                modal_id, self.get_conditions_table
            )

        return html

    def get_modal(self, modal_id, modal_body):
        template = loader.get_template("core/modal_base.html")
        country = Country.objects.get(country_code=self.country_code.upper())
        context = {
            "modal_id": modal_id,
            "modal_body": modal_body,
            "commodity_code_split": self.commodity_code_split,
            "measure_type": self.type_description,
            "commodity_description": self.commodity_title,
            "selected_origin_country_name": country.name,
        }
        rendered = template.render(context)
        return rendered

    @property
    def commodity_code_split(self):
        """
        Used to display the code in the template
        Splits the commodity code into 3 groups of 6 digits, 2 digits and 2 digits
        :return: list
        """
        code_match_obj = re.search(settings.COMMODITY_CODE_REGEX, self.commodity_code)
        return [code_match_obj.group(i) for i in range(1, 5)]

    @property
    def get_conditions_table(self):
        template = loader.get_template("hierarchy/measure_condition_table.html")
        measure_conditions = self.get_measure_conditions_by_measure_id(self.measure_id)
        context = {
            "column_headers": [
                "Condition code",
                "Condition",
                "Document code",
                "Requirement",
                "Action",
                "Duty",
            ],
            "conditions": measure_conditions,
        }
        rendered = template.render(context)
        return rendered

    @property
    def get_quota_table(self):
        template = loader.get_template("commodities/measure_quota_table.html")
        measure_quota = self.get_measure_quota_definition_by_order_number(
            self.di["order_number"]["number"]
        )

        context = {
            "quota_def": measure_quota,
            "geographical_area": self.get_geographical_area(),
        }

        rendered = template.render(context)
        return rendered

    def get_table_dict(self):
        country = self.geographical_area_description

        try:
            measure_description = (
                self.di["measure_type"]["description"],
                self.di["additional_code"],
            )
        except KeyError:
            measure_description = self.di["measure_type"]["description"]

        if self.di["order_number"]:
            order_str = self.quota_html()
            measure_description = measure_description + "\n" + order_str

        measure_value = self.di["duty_expression"]["base"]

        excluded_countries = ", ".join(
            [di["description"] for di in self.di["excluded_countries"]]
        )

        start_end_date = self.di["effective_start_date"][:10]
        if self.di.get("effective_end_date"):
            date_str = self.di["effective_end_date"][:10]
            start_end_date = start_end_date + "\n(%s)" % date_str

        return {
            "country": country,
            "measure_description": measure_description,
            "conditions_html": self.conditions_html,
            "measure_value": measure_value,
            "excluded_countries": excluded_countries,
            "start_end_date": start_end_date,
        }

    def quota_html(self):
        """
        generate an html link for quota order number that supports javascript enable modal and no javascript backup
        also generates the matching modal html and appends it to a class dictionary variable
        :return: the html of the link
        """
        html = ""
        order_number = self.di["order_number"]["number"]
        url = self.commodity_obj.get_quotas_url(
            self.country_code.lower(),
            self.measure_id,
            order_number,
        )

        modal_id = "{0}-{1}".format(self.measure_id, order_number)
        html = ' - <a data-toggle="modal" data-target="{0}" href="{1}">Order No: {2}</a>'.format(
            modal_id, url, order_number
        )

        if self.di["order_number"]["definition"] is None:
            modal_body = """<table class="govuk-table app-flexible-table">
                            <caption class="govuk-table__caption govuk-heading-m">Quota number : {0}</caption>
                            <tbody class="govuk-table__body app-flexible-table__body">
                            <tr class="govuk-table__row app-flexible-table__row">
                            <td class="govuk-table__cell app-flexible-table__cell govuk-!-font-weight-regular"
                                        scope="row"><p>{1}</p>
                            </td></tr></tbody></table>""".format(
                order_number, settings.QUOTA_DEFAULT_MESSAGE
            )
        else:
            modal_body = self.get_quota_table

        self.measures_modals[modal_id] = self.get_modal(modal_id, modal_body)

        return html

    def get_table_row(self):
        """
        generates the data for a table row for a commodities' measures table
        :return: returns a list
        """
        di = self.get_table_dict()
        data = [di[tup[0]] for tup in COMMODITY_DETAIL_TABLE_KEYS]
        data = self.rename_countries_default(data)

        try:
            data = self.reformat_date(data)
        except Exception as e:
            logger.debug("trying to reformat date from data, throws {0}".format(e.args))

        data_with_headings = []

        for index, value in enumerate(data):
            data_with_headings.append([COMMODITY_DETAIL_TABLE_KEYS[index][1], value])

        return data_with_headings

    def reformat_date(self, data):

        row_last_index = len(data) - 1
        pattern = "^((\d{4})-(\d{2})-(\d{2}))$|^((\d{4})-(\d{2})-(\d{2}))\s(\(((\d{4})-(\d{2})-(\d{2}))\))$"
        target = re.compile(pattern)
        matched = target.match(data[row_last_index])
        if not matched.group(9):
            start_date_obj = datetime.strptime(matched.group(1), "%Y-%m-%d")
            start_date_str = start_date_obj.strftime("%-d&nbsp;%B&nbsp;%Y")
            data[row_last_index] = start_date_str
        else:
            start_date_obj = datetime.strptime(matched.group(5), "%Y-%m-%d")
            start_date_str = start_date_obj.strftime("%-d&nbsp;%B&nbsp;%Y")
            end_date_obj = datetime.strptime(matched.group(10), "%Y-%m-%d")
            end_date_str = end_date_obj.strftime("%-d&nbsp;%B&nbsp;%Y")

            data[row_last_index] = "{0} ({1})".format(start_date_str, end_date_str)

        return data

    def rename_countries_default(self, data):
        if "ERGA OMNES" in data:
            idx = data.index("ERGA OMNES")
            data[idx] = "All countries"
        return data

    def get_measure_conditions(self):
        """
        get a list of conditions for the measure
        :return: list of dictionaries
        """
        return [MeasureCondition(di) for di in self.di["measure_conditions"]]

    def get_measure_conditions_by_measure_id(self, measure_id):
        """
        get a measure's condition by it's measure id
        :param measure_id: number
        :return: list of a single dictionary
        """

        return [
            condition
            for condition in self.get_measure_conditions()
            if condition.di["measure_id"] == measure_id
        ]

    def get_measure_quota_definition_by_order_number(self, order_number):
        """
        get a measure's quot definition by it's order_number
        :param order_number: string of a number
        :return: dictionary or None
        """
        if self.di["order_number"]["number"] == order_number:
            if self.di["order_number"]["definition"] and isinstance(
                self.di["order_number"]["definition"]["validity_start_date"], str
            ):
                self.di["order_number"]["definition"]["validity_start_date"] = parse_dt(
                    self.di["order_number"]["definition"]["validity_start_date"]
                )
            if self.di["order_number"]["definition"] and isinstance(
                self.di["order_number"]["definition"]["validity_end_date"], str
            ):
                self.di["order_number"]["definition"]["validity_end_date"] = parse_dt(
                    self.di["order_number"]["definition"]["validity_end_date"]
                )

            return self.di["order_number"]

    def get_geographical_area(self):
        """
        todo: check if used and remove if not
        :param country_code:
        :return:
        """
        if self.di["geographical_area"]:
            if self.di["geographical_area"]["description"] == "ERGA OMNES":
                return "All countries"
            else:
                return self.di["geographical_area"]["description"]


class MeasureCondition:
    def __init__(self, di):
        self.di = di

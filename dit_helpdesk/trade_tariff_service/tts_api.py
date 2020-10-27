import logging
import re
from datetime import datetime

from django.db import connection
from django.template import loader, Context
from dateutil.parser import parse as parse_dt
from django.conf import settings
from django.urls import reverse

from countries.models import Country

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)

DUTY_HTML_REGEX = r"<span.*>\s?(?P<duty>\d[\d\.]*?)\s?</span>"

COMMODITY_DETAIL_TABLE_KEYS = [
    ("country", "Country"),
    ("measure_description", "Measure type"),
    ("measure_value", "Value"),
    ("conditions_html", "Conditions"),
    # ("excluded_countries", "Excluded countries"),
    ("start_end_date", "Start date"),
]


class CommodityJson(object):
    def __init__(self, di):
        self.di = di

    def __repr__(self):
        return "CommodityJson"

    @property
    def title(self):
        return self.di["description"]

    @property
    def code(self):
        return self.di["goods_nomenclature_item_id"]

    @property
    def chapter_note(self):
        return self.di["chapter"]["chapter_note"]

    @property
    def chapter_title(self):
        return self.di["chapter"]["formatted_description"]

    @property
    def section_position(self):
        return self.di["section"]["position"]

    @property
    def duty_rate(self):
        duty_html = self.di["basic_duty_rate"]
        match = re.search(DUTY_HTML_REGEX, duty_html, flags=re.I)
        if match is None:
            return None
        return float(match.groupdict()["duty"])  # percentage

    def get_import_measures(self, origin_country, vat=None, excise=None):

        if "import_measures" not in self.di:
            return []

        measures = [
            ImportMeasureJson(d, self.code, self.title, origin_country)
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

    @property
    def footnotes(self):
        return self.di["footnotes"]


class ImportMeasureJson(object):
    def __init__(self, di, commodity_code, commodity_title, country_code):
        self.di = di
        self.commodity_code = commodity_code
        self.commodity_title = commodity_title
        self.measures_modals = {}
        self.country_code = country_code

    def get_commodity_sid(self):
        """
        get nomenclature sid direct from db. used by vue__conditions_html and vue__quota_html to build the correct url
        for modal fallback page
        :return:
        """

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT goods_nomenclature_sid "
                "FROM commodities_commodity "
                "WHERE commodity_code = %s "
                "AND description = %s",
                [self.commodity_code, self.commodity_title.replace("|", "")],
            )
            row = cursor.fetchone()
        if not row:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT goods_nomenclature_sid, description "
                    "FROM commodities_commodity "
                    "WHERE commodity_code = %s",
                    [self.commodity_code],
                )
                row = cursor.fetchone()
        return row

    @classmethod
    def get_date(cls, di, key):
        dt_str = di.get(key)
        if dt_str is None:
            return None
        return parse_dt(dt_str)

    def __repr__(self):
        return "ImportMeasureJson %s %s" % (self.commodity_code, self.type_id)

    @property
    def is_import(self):
        return self.di["import"]

    @property
    def origin(self):
        return self.di["origin"]  # e.g. "uk"

    @property
    def effective_start_date(self):
        return self.get_date(self.di, "effective_start_date")

    @property
    def effective_end_date(self):
        return self.get_date(self.di, "effective_end_date")

    @property
    def geographical_area(self):
        """"
        one GA per measure
        if everywhere in the world outside the EU return ERGA OMNES

        """

        if self.di["geographical_area"]["description"] == "ERGA OMNES":
            return "ERGA OMNES"
        # NOTE: when filtering by a GA, you will need to search
        # both the top-level and any children in case the country exists
        # import pdb; pdb.set_trace()

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
    def conditions_summary(self):
        """
        list of conditions (e.g. you can import if you have document X)
        other keys: 'condition_code', 'condition', 'document_code', '
        requirement', 'action', 'duty_expression'
        """
        return [di["condition"] for di in self.di["measure_conditions"]]

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
    def order_number_definition_summary(self):
        if not self.di.get("order_number"):
            return None
        status = self.di["order_number"]["definition"]["status"]
        description = self.di["order_number"]["definition"]["description"]
        return status, description

    @property
    def num_conditions(self):
        return len(self.di["measure_conditions"])

    def is_relevant_for_origin_country(self, origin_country_code):
        geo_area = self.di["geographical_area"]
        if geo_area is not None:
            if (
                geo_area["id"][0].isalpha()
                and geo_area["id"] == origin_country_code.upper()
            ):
                return True
            for child_area in geo_area["children_geographical_areas"]:
                if (
                    child_area["id"][0].isalpha()
                    and child_area["id"] == origin_country_code.upper()
                ):
                    return True
            return False

    @property
    def vue__legal_base_html(self):

        if not self.di.get("legal_acts", []):  # todo: make this a property method
            return "-"
        hrefs = []
        for d in self.di["legal_acts"]:
            reg_url, reg_code = d["regulation_url"], d["regulation_code"]
            hrefs.append('<a href="%s">%s</a>' % (reg_url, reg_code))
        return ", ".join(hrefs)

    @property
    def vue__conditions_html(self):

        if not self.num_conditions:
            html = "-"
        else:
            commodity_sid = self.get_commodity_sid()
            url = "{0}/import-measure/{1}/conditions".format(
                commodity_sid[0], self.measure_id
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
        country = Country.objects.get(country_code=self.country_code)
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
        template = loader.get_template("commodities/measure_condition_table.html")
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

    @property
    def vue__footnotes_html(self):
        # {'code': 'CD550', 'description': 'Eligibility to benefit from this tariff quota shall be subject to the
        # presentation of an import licence AGRIM and a declaration of origin issued in accordance with Regulation
        # (EU) 2017/1585.', 'formatted_description': 'Eligibility to benefit from this tariff quota shall be subject
        # to the presentation of an import licence AGRIM and a declaration of origin issued in accordance with
        # Regulation (EU) 2017/1585.'}
        if not self.di["footnotes"]:
            return "-"

        hrefs = []
        for d in self.di["footnotes"]:
            code, url = d["code"], "#"
            hrefs.append('<a href="%s">%s</a>' % (url, code))
        return ", ".join(hrefs)

    def get_table_dict(self):

        country = self.di["geographical_area"]["description"]

        if self.di["geographical_area"]["id"][0].isalpha():
            country = country + " (%s)" % self.di["geographical_area"]["id"]

        try:
            measure_description = (
                self.di["measure_type"]["description"],
                self.di["additional_code"],
            )
        except KeyError:
            measure_description = self.di["measure_type"]["description"]

        if self.di["order_number"]:
            order_str = self.vue__quota_html()
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
            "conditions_html": self.vue__conditions_html,
            "measure_value": measure_value,
            "excluded_countries": excluded_countries,
            "start_end_date": start_end_date,
            "legal_base_html": self.vue__legal_base_html,
            "footnotes_html": self.vue__footnotes_html,
        }

    def vue__quota_html(self):
        """
        generate an html link for quota order number that supports javascript enable modal and no javascript backup
        also generates the matching modal html and appends it to a class dictionary variable
        :return: the html of the link
        """
        commodity_sid = self.get_commodity_sid()[0]
        html = ""
        order_number = self.di["order_number"]["number"]
        if commodity_sid:
            url = "{0}/import-measure/{1}/quota/{2}".format(
                commodity_sid, self.measure_id, order_number
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


class MeasureCondition(object):
    def __init__(self, di):
        self.di = di


class ChapterJson(object):
    def __init__(self, di):
        self.di = di

    @property
    def title(self):
        return self.di["formatted_description"]

    @property
    def harmonized_code(self):
        return self.di["goods_nomenclature_item_id"]

    @property
    def heading_ids(self):
        return [di["goods_nomenclature_item_id"][:4] for di in self.di["headings"]]

    @property
    def heading_urls(self):
        return [settings.HEADING_URL % id for id in self.heading_ids]

    @property
    def chapter_note(self):
        if self.di and "chapter_note" in self.di.keys():
            return self.di["chapter_note"]
        return ""


class HeadingJson(object):
    def __init__(self, di):
        self.di = di

    @property
    def title(self):
        return self.di["formatted_description"].replace("&nbsp;", " ").strip()

    @property
    def code(self):
        return self.di["goods_nomenclature_item_id"]

    @property
    def commodity_dicts(self):
        return [di for di in self.di.get("commodities", [])]

    @property
    def commodity_ids(self):
        if "commodities" not in self.di:
            tup = (self.code, self.title)
            logger.debug('warning: no commodities found for Heading: %s "%s"' % tup)
            return []

        return [
            (di["goods_nomenclature_item_id"], di["leaf"])
            for di in self.di["commodities"]
        ]

    @property
    def commodity_urls(self):
        return [
            ((settings.COMMODITY_URL % _id), is_leaf)
            for (_id, is_leaf) in self.commodity_ids
        ]

    def get_import_measures(self, origin_country, vat=None, excise=None):

        measures = [
            ImportMeasureJson(d, self.code, self.title, origin_country)
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

    @property
    def footnotes(self):
        if not isinstance(self.di, str) and "footnotes" in self.di.keys():
            return self.di["footnotes"]
        else:
            return []

    def get_import_measure_by_id(self, measure_id, country_code=None):

        measures = [
            measure
            for measure in self.get_import_measures(country_code)
            if measure.measure_id == measure_id
        ]

        return measures[0] if len(measures) == 1 else None


class SubHeadingJson(object):
    def __init__(self, di):
        self.di = di

    @property
    def title(self):
        return self.di["formatted_description"].replace("&nbsp;", " ").strip()

    @property
    def code(self):
        return self.di["goods_nomenclature_item_id"]

    @property
    def commodity_dicts(self):
        return [di for di in self.di.get("commodities", [])]

    @property
    def commodity_ids(self):
        if "commodities" not in self.di:
            tup = (self.code, self.title)
            logger.debug('warning: no commodities found for Heading: %s "%s"' % tup)
            return []

        return [
            (di["goods_nomenclature_item_id"], di["leaf"])
            for di in self.di["commodities"]
        ]

    @property
    def commodity_urls(self):
        return [
            ((settings.COMMODITY_URL % _id), is_leaf)
            for (_id, is_leaf) in self.commodity_ids
        ]

    @property
    def footnotes(self):
        if not isinstance(self.di, str) and "footnotes" in self.di.keys():
            return self.di["footnotes"]
        else:
            return []

    def get_import_measures(self, origin_country, vat=None, excise=None):

        measures = []

        if not isinstance(self.di, str) and "import_measures" in self.di.keys():
            measures = [
                ImportMeasureJson(d, self.code, self.title, origin_country)
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

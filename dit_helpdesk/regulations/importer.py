import json
import logging
import pandas

from pathlib import Path
from numpy import nan

from django.conf import settings

from commodities.models import Commodity
from hierarchy.models import SubHeading, Heading
from regulations.models import Regulation, RegulationGroup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def data_loader(file_path):
    """
    opens source file at filepath and reads data into either dictionary object or pandas dataframe object
    :param file_path: path to file
    :return: data_frame or dictionary
    """

    extension = Path(file_path).suffix

    if extension == ".json":
        with open(file_path) as f:
            json_data = json.load(f)
        return json_data
    else:
        with open(file_path) as f:
            data_frame = pandas.read_csv(f, encoding="utf8")
        return data_frame


def data_writer(file_path, data):
    """
    takes a filepath and data object and writes the data to a file at the filepath
    :param file_path: path to file
    :param data: data to write to the file
    """

    outfile = open(file_path, "w+")
    json.dump(data, outfile)


class RegulationsImporter:
    """
    Import regulations and their related document title and urls attached to appropriate hierarchy
    heading and commodity leaf items
    """

    def __init__(self):
        self.data = []
        self.documents = None
        self.data_path = settings.REGULATIONS_DATA_PATH

    def instance_builder(self, data_map):
        """
        receive a dictionary item
        find appropriate heading, subheading or commodity parent items for the regulation item
        create the regulation item
        set the M2M parent relationships for regulation
        create document item for the regulation
        set the relationship for

        :param data_map: eg. {"parent_codes": [], "title": "title", "document" {"url": "url", "title": "title"}}
        :return:
        """

        parent_headings = self.get_heading_parents(data_map)

        parent_commodities = self.get_commodity_parents(data_map)

        parent_subheadings = self.get_subheading_parents(parent_commodities, data_map)

        regulation_group_field_data = {"title": data_map["title"]}

        regulation_group = self._create_instance(RegulationGroup, regulation_group_field_data)
        regulation_group.headings.add(*list(parent_headings))
        regulation_group.commodities.add(*list(parent_commodities))
        regulation_group.subheadings.add(*list(parent_subheadings))

        if data_map["document"]["url"] is None:
            data_map["document"]["url"] = ""
        kwargs = {
            "url": data_map["document"]["url"],
        }
        defaults = {
            "celex": data_map["document"]["celex"],
            "title": data_map["document"]["title"],
        }
        regulation = self._create_instance(Regulation, kwargs, defaults=defaults)
        regulation.regulation_groups.add(regulation_group)
        regulation.save()

    @staticmethod
    def get_subheading_parents(commodities, data_map):
        """
        filter out the subheading codes from the list of parent codes. i.e. those codes that do not found in the list
        of commodity item codes
        return a queryset of subheading items based on the filtered list
        :param commodities: list of parent commodity items found
        :param data_map: regulation item data
        :return: subheading items
        """
        seen_codes = [commodity.commodity_code for commodity in commodities]
        missed_codes = [
            code for code in data_map["parent_codes"] if code not in seen_codes
        ]
        subheadings = SubHeading.objects.filter(commodity_code__in=missed_codes)
        return subheadings

    @staticmethod
    def get_heading_parents(data_map):
        """
        return a queryset of heading items if any data_map[parent_codes] match
        :param data_map: regulation item data
        :return: heading items
        """
        headings = Heading.objects.filter(heading_code__in=data_map["parent_codes"])
        return headings

    @staticmethod
    def get_commodity_parents(data_map):
        """
        return a queryset of commodity items if any data_map[parent_codes] match
        :param data_map:
        :return:
        """
        commodities = Commodity.objects.filter(
            commodity_code__in=data_map["parent_codes"]
        )
        return commodities

    def _create_instance(self, model_class, field_data, defaults=None):
        """
        get or create an instance of <model_name> with <field_data> and return the create instance
        :param model_name: model name of the instance to create
        :param field_data: data create the instance with
        :return: existing or created instance
        """

        instance, created = model_class.objects.update_or_create(defaults, **field_data)
        if created:
            logger.info("%s instance created", model_class.__name__)
        else:
            logger.info("Returning existing %s", model_class.__name__)
        return instance

    @staticmethod
    def _normalise_commodity_code(commodity_id):
        """
        Where a commodity code is only 9 digits convert to a a string prepend a zero
        :param commodity_id: int of commodity id to normalise
        :return:
        """
        if len(str(commodity_id)) == 9:
            commodity_code = "0{0}".format(commodity_id)
        else:
            commodity_code = str(commodity_id)
        return commodity_code

    def load(self, data_path=None):
        """
        Load data from files
        :param data_path:
        :return:
        """

        if data_path:

            product_regulations = data_loader(
                data_path.format("product_specific_regulations.csv")
            )

            commodity_regulations_map = json.loads(
                data_loader(data_path.format("product_reqs_v2.csv")).to_json(
                    orient="records"
                )
            )
            document_urls_title_map = data_loader(
                data_path.format("urls_with_text_description.json")
            )

            regulations_data = self.clean_and_extend_regulations_data(
                document_urls_title_map, product_regulations
            )

            titles_to_codes_map = self.build_titles_to_codes_map(
                commodity_regulations_map
            )

            self.data = self.build_list_of_regulation_maps(
                regulations_data, titles_to_codes_map
            )

    def process(self):
        """
        loop through a list of dictionaries filtering out those whose title attribute is None and pass to the
        instance builder method
        """
        for regulation_map in self.data:
            if not regulation_map["document"]["title"] is None:
                self.instance_builder(regulation_map)

    @staticmethod
    def clean_and_extend_regulations_data(documents, regulations):
        """
        add a column for the corresponding title for each url and None if the url field is empty
        returns list of regulations each with a corresponding document url and title
        e.g. "regulations_title", "document_url", "document_title"
        :param documents: document url and title map
        :param regulations: table of regulation titles with urls
        :return: return list of regulations each with a corresponding document url and title
        """
        regulations_table = regulations[["Title", "CELEX", "UK Reg"]]
        regulations_table.columns = ["title", "celex", "url"]
        regulations_table = regulations_table.to_dict("records")

        for item in regulations_table:
            if item["url"] is not nan and item["url"] in documents.keys():
                item["document_title"] = documents[item["url"]]
            else:
                item["document_title"] = None
                item["url"] = None

        return regulations_table

    def build_list_of_regulation_maps(self, data_table, titles_to_codes_map):
        """
        build a list of dictionaries
        eg. [{"parent_codes": [], "title": "title", "document" {"url": "url", "title": "title"}},]

        :param data_table: list of dictionaries [{"celex": ..., "reg": ..., "document_title": ..., "url': ...}, ...]
        :param titles_to_codes_map: e.g. {"commodity_title": ["list", "of", "code"], ...}
        :return: list of dictionaries
        """
        map_list = []
        for item in data_table:
            title = item["title"]
            try:
                parent_codes = [
                    self._normalise_commodity_code(code)
                    for code in titles_to_codes_map[title]
                ]

                if title in titles_to_codes_map.keys():
                    map_list.append(
                        {
                            "parent_codes": parent_codes,
                            "title": item["title"],
                            "document": {
                                "celex": item["celex"],
                                "url": item["url"],
                                "title": item["document_title"],
                            },
                        },
                    )
            except KeyError as key_err:
                logger.debug(
                    "Missing regulations documents for %s",
                    item["title"],
                    exc_info=key_err,
                )

        return map_list

    @staticmethod
    def build_titles_to_codes_map(commodity_titles):
        """
        builds a map of a list of commodity codes associated with each regulation title
        returns a dictionary keyed on regulation title
        e.g.
        {"commodity_title": ["list", "of", "code"], ...}
        :param commodity_titles: table of a list of regulation titles for each commodity code
        :return: dictionary
        """
        data_map = {}
        for commodity in commodity_titles:
            for document in commodity["Documents"].split("|"):
                doc_title = document.strip()
                if doc_title in data_map.keys() and isinstance(
                    data_map[doc_title], list
                ):
                    data_map[doc_title].append(commodity["Commodity code"])
                else:
                    data_map[doc_title] = [commodity["Commodity code"]]
        return data_map

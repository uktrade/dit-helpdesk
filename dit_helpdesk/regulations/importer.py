import json
import logging
from pathlib import Path

import pandas
from django.apps import apps
from django.conf import settings
from numpy import nan

from commodities.models import Commodity
from hierarchy.models import SubHeading

logger = logging.getLogger(__name__)


def data_loader(file_path):

    """
    :param file_path:
    :return:
    """

    extension = Path(file_path).suffix

    if extension == '.json':
        with open(file_path) as f:
            json_data = json.load(f, )
        return json_data
    else:
        with open(file_path) as f:
            data_frame = pandas.read_csv(f, encoding='utf8')
        return data_frame


def data_writer(file_path, data):
    """
    :param file_path:
    :param data:
    :return:
    """

    outfile = open(file_path, 'w+')
    json.dump(data, outfile)


class RegulationsImporter:
    """

    """

    def __init__(self):
        self.data = []
        self.documents = None
        self.app_label = __package__.rsplit('.', 1)[-1]
        self.data_path = settings.REGULATIONS_DATA_PATH
        self.missing_commodities = []

    def instance_builder(self, data_map):

        parent_commodities = self.get_commodity_parents(data_map)

        parent_subheadings = self.get_subheading_parents(parent_commodities, data_map)

        regulation_field_data = {"title": data_map['title']}

        regulation = self._create_instance("Regulation", regulation_field_data)
        regulation.commodities.add(*list(parent_commodities))
        regulation.subheadings.add(*list(parent_subheadings))

        if data_map['document']['url'] is None:
            data_map['document']['url'] = ''
        document = self._create_instance("Document", data_map['document'])
        document.regulations.add(regulation)
        document.save()

        print(regulation, document.regulations.all())

    @staticmethod
    def get_subheading_parents(commodities, data_map):
        seen_codes = [commodity.commodity_code for commodity in commodities]
        missed_codes = [code for code in data_map['parent_codes'] if code not in seen_codes]
        subheadings = SubHeading.objects.filter(commodity_code__in=missed_codes)
        return subheadings

    @staticmethod
    def get_commodity_parents(data_map):
        commodities = Commodity.objects.filter(commodity_code__in=data_map['parent_codes'])
        return commodities

    def _create_instance(self, model_name, field_data):

        model = apps.get_model(app_label=self.app_label, model_name=model_name)

        instance, created = model.objects.get_or_create(
            **field_data
        )
        if created:
            print("{0} instance created".format(model_name))
        else:
            print("Returning existing {0}".format(model_name))
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

        if data_path:

            regulations = data_loader(data_path.format('product_specific_regulations.csv'))

            commodity_code_titles = json.loads(data_loader(data_path.format('product_reqs_v2.csv')
                                                           ).to_json(orient='records'))
            documents = data_loader(data_path.format('urls_with_text_description.json'))

            regulations_data = self.clean_and_extend_regulations_data(documents, regulations)

            titles_to_codes_map = self.build_titles_to_codes_map(commodity_code_titles)

            self.data = self.build_list_of_regulation_maps(regulations_data, titles_to_codes_map)

    def process(self):
        for regulation_map in self.data:
            self.instance_builder(regulation_map)

    @staticmethod
    def clean_and_extend_regulations_data(documents, regulations_data):
        data_table = regulations_data[['Title', 'UK Reg']].values.tolist()
        for item in data_table:
            if item[1] is not nan:
                item.append(documents[item[1]])
            else:
                item[1] = None
                item.append(None)
        return data_table

    def build_list_of_regulation_maps(self, data_table, titles_to_codes_map):
        map_list = []
        for item in data_table:
            try:
                parent_codes = [self._normalise_commodity_code(code) for code in titles_to_codes_map[item[0]]]

                if item[0] in titles_to_codes_map.keys():
                    map_list.append(
                        {
                            "parent_codes": parent_codes,
                            "title": item[0],
                            "document": {
                                "url": item[1],
                                "title": item[2]
                            }
                        }
                    )
            except KeyError as key_err:
                logger.info("Missing regulations documents for {0}: with error {1} ".format(item[0], key_err.args))

        return map_list

    @staticmethod
    def build_titles_to_codes_map(commodity_titles):
        data_map = {}
        for commodity in commodity_titles:
            for document in commodity['Documents'].split('|'):
                doc_title = document.strip()
                if doc_title in data_map.keys() and isinstance(data_map[doc_title], list):
                    data_map[doc_title].append(commodity['Commodity code'])
                else:
                    data_map[doc_title] = [commodity['Commodity code']]
        return data_map

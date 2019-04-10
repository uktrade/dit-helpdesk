import json
import sys
from pathlib import Path
from pprint import pprint

import pandas
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import _get_queryset
from commodities.models import Commodity
from hierarchy.models import Section, SubHeading, Heading, Chapter
from regulations.models import Regulation, Document
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_object_or_none(klass, *args, **kwargs):
  queryset = _get_queryset(klass)
  try:
    return queryset.get(*args, **kwargs)
  except queryset.model.DoesNotExist:
    return None


class RegulationsImporter:

    def __init__(self):
        self.data = []
        self.documents = None
        self.app_label = __package__.rsplit('.', 1)[-1]
        self.data_path = settings.REGULATIONS_DATA_PATH
        self.missing_commodities = []

    def data_loader(self, file_path):

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

    def data_writer(self, file_path, data):
        """
        :param file_path:
        :param data:
        :return:
        """

        outfile = open(file_path, 'w+')
        json.dump(data, outfile)

    def instance_builder(self, regulations, item_data):

        item_data = self._rename_key(item_data, "Commodity code", "commodity_id")

        commodity_code = self._normalise_commodity_code(item_data['commodity_id'])
        # commodity = get_object_or_none(Commodity, commodity_code=commodity_code)
        parent_item = self.get_parent_item_or_none(commodity_code)
        section = self.get_section_or_none(parent_item)

        titles = list(regulations.Title)
        types = list(regulations.Type)
        celexes = list(regulations.CELEX)
        urls = list(regulations['UK Reg'])

        document_titles = [doc.strip() for doc in item_data["Documents"].split('|')]

        try:
            for item in document_titles:
                for idx, title in enumerate(titles):
                    if not isinstance(urls[idx], float) and title == item:
                        regulation_field_data = {"title": title}

                        regulation = self._create_instance("Regulation", regulation_field_data)

                        document_field_data = {
                            "title": self.documents[urls[idx]],
                            "type": types[idx],
                            "celex": celexes[idx],
                            "url": urls[idx]
                        }

                        document = self._create_instance("Document", document_field_data)

                        document.regulations.add(regulation)
                        document.save()

                        if parent_item._meta.model_name == "commodity":
                            regulation.commodities.add(parent_item)
                        elif parent_item._meta.model_name == "subheading":
                            regulation.subheadings.add(parent_item)
                        elif parent_item._meta.model_name == "heading":
                            regulation.headings.add(parent_item)
                        elif parent_item._meta.model_name == "chapter":
                            regulation.chapters.add(parent_item)
                        else:
                            print("niether chapter, heading, subheading nor commodity")

                        regulation.sections.add(section)
                        regulation.save()

        except Exception as ex:
            print(ex.args)
            self.missing_commodities.append(commodity_code)
        self.data_writer(self.data_path.format('missing_commodities.json'), self.missing_commodities)

    def _create_instance(self, model_name, field_data):

        model = apps.get_model(app_label=self.app_label, model_name=model_name)

        instance, created = model.objects.get_or_create(
            **field_data
        )
        if created:
            print("{0} instance created".format(model_name))
        else:
            print("{0} instance already exists".format(model_name))
        return instance

    def _normalise_commodity_code(self, commodity_id):
        """
        Where a commodity code is only 9 digits prepend a zero
        :param item_data: the dictioanry to work with
        :return:
        """
        if len(str(commodity_id)) == 9:
            commodity_code = "0{0}".format(commodity_id)
        else:
            commodity_code = str(commodity_id)
        return commodity_code

    def _rename_key(self, old_dict, old_name, new_name):
        """
        rename a dictionary key
        :param old_dict: the dictioanry to work on
        :param old_name: the old key name
        :param new_name: the new key name
        :return: dictionary
        """
        new_dict = {}
        for key, value in zip(old_dict.keys(), old_dict.values()):
            new_key = key if key != old_name else new_name
            new_dict[new_key] = old_dict[key]
        return new_dict

    def load(self, data_path=None):

        if data_path:

            regulations_data = self.data_loader(data_path.format('product_specific_regulations.csv'))

            commodity_titles = json.loads(self.data_loader(data_path.format('product_reqs_v2.csv')
                                                           ).to_json(orient='records'))
            self.documents = self.data_loader(data_path.format('urls_with_text_description.json'))

            for item in commodity_titles:
                self.data.append(self.instance_builder(regulations_data, item))

    def get_parent_item_or_none(self, commodity_code):

        try:
            item = Commodity.objects.filter(commodity_code=commodity_code).first()
            if item is None:
                item = SubHeading.objects.filter(commodity_code=commodity_code).first()
                if item is None:
                    item = Heading.objects.filter(heading_code=commodity_code).first()
                    if item is None:
                        item = Chapter.objects.filter(chapter_code=commodity_code).first()
        except ObjectDoesNotExist as odne:
            print(odne.args)
            sys.exit()
        return item

    def get_section_or_none(self, parent_item):

        model_name = parent_item._meta.model_name

        try:
            if model_name == "commodity":
                heading_obj = parent_item.get_heading()
            elif model_name == "subheading":
                heading_obj = parent_item.get_parent()
                while type(heading_obj) is not Heading:
                    heading_obj = heading_obj.get_parent()
            else:
                heading_obj = parent_item
        except Exception as ex:
            print(ex.args)
            sys.exit()

        return heading_obj.chapter.section

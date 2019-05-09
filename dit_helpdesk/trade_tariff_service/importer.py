import json
import logging
import sys

import requests
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from commodities.models import Commodity
from hierarchy.models import Section, Chapter, Heading, SubHeading

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)

hierarchy_model_map = {
    "Commodity": {
        "file_name": "hierarchy_subheading_commodities.json",
        "app_name": "commodities"
    },
    "Chapter": {
        "file_name": "hierarchy_subheading_chapters.json",
        "app_name": "hierarchy"
    },
    "Heading": {
        "file_name": "hierarchy_subheading_headings.json",
        "app_name": "hierarchy"
    },
    "SubHeading": {
        "file_name": "hierarchy_subheading_subheadings.json",
        "app_name": "hierarchy"
    },
    "Section": {
        "file_name": "hierarchy_subheading_sections.json",
        "app_name": "hierarchy"
    }
}


class HierarchyBuilder:

    def __init__(self):
        self.data = {
            "Commodity": {
                "data": {},
                "objects": []
            },
            "Section": {
                "data": {},
                "objects": []
            },
            "Heading": {
                "data": {},
                "objects": []
            },
            "SubHeading": {
                "data": {},
                "objects": []
            },
            "Chapter": {
                "data": {},
                "objects": []
            }
        }

    @staticmethod
    def file_loader(model_name):

        file_name = hierarchy_model_map[model_name]['file_name']
        file_path = settings.IMPORT_DATA_PATH.format(file_name)

        with open(file_path) as f:
            json_data = json.load(f)
        return json_data

    @staticmethod
    def rename_key(old_dict, old_name, new_name):
        new_dict = {}
        for key, value in zip(old_dict.keys(), old_dict.values()):
            new_key = key if key != old_name else new_name
            new_dict[new_key] = old_dict[key]
        return new_dict

    def instance_builder(self, model, data):

        if model is Section:
            data = self.rename_key(data, 'child_goods_nomenclature_sids', 'tts_json')
        elif model is Chapter:
            parent = self.lookup_parent(Section, data['goods_nomenclature_sid'])
            if parent is not None:
                data["section_id"] = parent.pk
            data = self.rename_key(data, 'goods_nomenclature_item_id', 'chapter_code')
        elif model is Heading:
            parent = self.lookup_parent(Chapter, data['parent_goods_nomenclature_sid'])
            if parent is not None:
                data['chapter_id'] = parent.pk
            data = self.rename_key(data, 'goods_nomenclature_item_id', 'heading_code')
        elif model is SubHeading:
            parent = self.lookup_parent(Heading, data['goods_nomenclature_sid'])
            if parent is not None:
                data['heading_id'] = parent.pk
            data = self.rename_key(data, 'goods_nomenclature_item_id', 'commodity_code')
            data = self.rename_key(data, 'leaf', 'tts_is_leaf')
        elif model is Commodity:
            heading_parent = self.lookup_parent(Heading, data['goods_nomenclature_sid'])
            subheading_parent = self.lookup_parent(SubHeading, data['goods_nomenclature_sid'])
            if heading_parent is not None:
                data['heading_id'] = heading_parent.pk
            if subheading_parent is not None:
                data['parent_subheading_id'] = subheading_parent.pk
            data = self.rename_key(data, 'goods_nomenclature_item_id', 'commodity_code')
            data = self.rename_key(data, 'leaf', 'tts_is_leaf')

        instance = model(**data)
        return instance

    # def check_model_names(self, model_names):
    #     return set([name in hierarchy_model_map.keys() for name in model_names])

    def data_scanner(self, model_names=None):

        if model_names is None:
            model_names = []

        for model_name in model_names:

            # if model_name == "Section":
            #     self.get_section_data_from_api()

            json_data = self.load_data(model_name)

            model = apps.get_model(app_label=hierarchy_model_map[model_name]["app_name"], model_name=model_name)

            for data in json_data:
                instance = self.instance_builder(model, data)
                if isinstance(instance, model):
                    self.data[model_name]["objects"].append(self.instance_builder(model, data))
            if len(self.data[model_name]["data"]) == len(self.data[model_name]["objects"]):
                model.objects.bulk_create(self.data[model_name]["objects"])
            else:
                sys.exit()

    def load_data(self, model_name):
        json_data = self.file_loader(model_name)
        self.data[model_name]["data"] = json_data
        return json_data

    @staticmethod
    def get_section_data_from_api():
        retry = []
        data = []
        urls = []

        def poll_api(url_list):
            for url in url_list:
                resp = requests.get(url)
                if resp.status_code == 200:
                    section = {}
                    section["section_id"] = resp.json()["id"]
                    section["roman_numeral"] = resp.json()["numeral"]
                    section["title"] = resp.json()["title"]
                    section["child_goods_nomenclature_sids"] = [chapter["goods_nomenclature_sid"]
                                                                for chapter in resp.json()["chapters"]]
                    section["position"] = resp.json()["position"]
                    data.append(section)
                else:
                    print("RESPONSE: ", resp.status_code)
                    retry.append(url)

        for i in range(1, 22):
            urls.append(settings.SECTION_URL.format(i))

        poll_api(urls)

        with open(settings.IMPORT_DATA_PATH.format("hierarchy_subheading_sections.json"), 'w') as outfile:
            json.dump(data, outfile)

    def lookup_parent(self, model, code):

        for item in self.data[model.__name__]["data"]:
            if model is Section:
                if int(code) in item["child_goods_nomenclature_sids"]:
                    return Section.objects.get(section_id=int(item["section_id"]))
            else:
                try:
                    return model.objects.get(goods_nomenclature_sid=code)
                except ObjectDoesNotExist as exception:
                    logger.debug(exception.args)
                    return None

    @staticmethod
    def process_orphaned_subheadings():

        subheadings = SubHeading.objects.filter(heading_id=None, parent_subheading_id=None)

        count = 0
        for subheading in subheadings:
            parent_sid = subheading.parent_goods_nomenclature_sid
            parent = SubHeading.objects.get(goods_nomenclature_sid=parent_sid)
            subheading.parent_subheading_id = parent.pk
            subheading.save()
            count = count + 1
        return count

    @staticmethod
    def process_orphaned_commodities():

        commodities = Commodity.objects.filter(heading_id=None, parent_subheading_id=None)

        for commodity in commodities:
            parent_sid = commodity.parent_goods_nomenclature_sid
            try:
                parent = SubHeading.objects.get(goods_nomenclature_sid=parent_sid)
                commodity.parent_subheading_id = parent.pk
            except ObjectDoesNotExist as exception:
                logger.debug(exception.args)
                parent = Heading.objects.get(goods_nomenclature_sid=parent_sid)
                commodity.heading_id = parent.pk
            commodity.save()

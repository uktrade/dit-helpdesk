import csv
import json
import logging
import os
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
    "Commodity": {"file_name": "prepared/commodities.json", "app_name": "commodities"},
    "Chapter": {"file_name": "prepared/chapters.json", "app_name": "hierarchy"},
    "Heading": {"file_name": "prepared/headings.json", "app_name": "hierarchy"},
    "SubHeading": {"file_name": "prepared/sub_headings.json", "app_name": "hierarchy"},
    "Section": {"file_name": "prepared/sections.json", "app_name": "hierarchy"},
}


class HierarchyBuilder:
    def __init__(self):
        self.data = {
            "Commodity": {"data": {}, "objects": []},
            "Section": {"data": {}, "objects": []},
            "Heading": {"data": {}, "objects": []},
            "SubHeading": {"data": {}, "objects": []},
            "Chapter": {"data": {}, "objects": []},
        }
        self.sections = []
        self.chapters = []
        self.headings = []
        self.commodities = []
        self.heading_codes = []

    @staticmethod
    def file_loader(model_name):
        """
        given a model name load json data from the file system to import
        :param model_name:
        :return:
        """

        file_name = hierarchy_model_map[model_name]["file_name"]
        file_path = settings.IMPORT_DATA_PATH.format(file_name)

        with open(file_path) as f:
            json_data = json.load(f)
        return json_data

    @staticmethod
    def rename_key(old_dict, old_name, new_name):
        """
        rename a key in a dictionary and return the new dictionary
        :param old_dict:
        :param old_name:
        :param new_name:
        :return:
        """
        new_dict = {}
        for key, value in zip(old_dict.keys(), old_dict.values()):
            new_key = key if key != old_name else new_name
            new_dict[new_key] = old_dict[key]
        return new_dict

    def instance_builder(self, model, data):
        """
        build an instance of a model provided the model type and data supplied and return the new instance
        :param model:
        :param data:
        :return:
        """
        parent = self.get_instance_parent(data, model)
        instance_data = self.get_instance_data(data, model, parent)
        return model(**instance_data) if instance_data else None

    def get_instance_data(self, data, model, parent):
        """
        Prepare an instance data dictionary for the supplied model using the supplied data and parent instance
        :param data: the data object from the api
        :param model: the model type that will be created
        :param parent: the parent instance for the instance being created
        :return: dictionary used to create the instance
        """
        instance_data = {}

        if model is Section:

            instance_data = self.rename_key(
                data, "child_goods_nomenclature_sids", "tts_json"
            )

        elif model is Chapter:

            if parent is not None:
                data["section_id"] = parent.pk

            instance_data = self.rename_key(
                data, "goods_nomenclature_item_id", "chapter_code"
            )

        elif model is Heading:

            if parent is not None:
                data["chapter_id"] = parent.pk

            instance_data = self.rename_key(
                data, "goods_nomenclature_item_id", "heading_code"
            )

        elif model is SubHeading:

            if parent is not None:
                data["heading_id"] = parent.pk

            instance_data = self.rename_key(
                data, "goods_nomenclature_item_id", "commodity_code"
            )

        elif model is Commodity:

            if parent is not None:
                if parent.__class__.__name__ is "Heading":
                    data["heading_id"] = parent.pk
                else:
                    data["parent_subheading_id"] = parent.pk

            data = self.rename_key(data, "goods_nomenclature_item_id", "commodity_code")
            instance_data = self.rename_key(data, "leaf", "tts_is_leaf")

        return instance_data

    def get_instance_parent(self, data, model):
        """
        return the parent instance for the supplied model and data
        :param data: data of the instance being created
        :param model: model type of instance being created
        :return: parent instance for the moel being created
        """
        parent = None
        if model is Chapter:
            parent = self.lookup_parent(Section, data["goods_nomenclature_sid"])

        elif model is Heading:
            parent = self.lookup_parent(Chapter, data["parent_goods_nomenclature_sid"])

        elif model is SubHeading:
            parent = self.lookup_parent(Heading, data["goods_nomenclature_sid"])

        elif model is Commodity:
            try:
                parent = self.lookup_parent(Heading, data["goods_nomenclature_sid"])
            except ObjectDoesNotExist as exception:
                logger.info("No Heading for commodity: {0}".format(exception.args))
                parent = self.lookup_parent(SubHeading, data["goods_nomenclature_sid"])
        return parent

    def data_scanner(self, model_names=None):
        """
        loop through models, loading json import data, build model instances from json data and commit instances
        to the database
        :param model_names:
        :return:
        """

        if model_names is None:
            model_names = []

        for model_name in model_names:
            logger.info("creating {0} instances".format(model_name))

            json_data = self.load_data(model_name)

            model = apps.get_model(
                app_label=hierarchy_model_map[model_name]["app_name"],
                model_name=model_name,
            )

            for data in json_data:
                instance = self.instance_builder(model, data)
                if isinstance(instance, model):
                    logger.info("CODE: storing instance {0}".format(str(instance)))
                    self.data[model_name]["objects"].append(instance)

            logger.info(
                "CODE: model data items {0} == model instances {1}".format(
                    len(self.data[model_name]["data"]),
                    len(self.data[model_name]["objects"]),
                )
            )

            if len(self.data[model_name]["data"]) == len(
                self.data[model_name]["objects"]
            ):
                logger.info("CODE: creating instances")
                model.objects.bulk_create(self.data[model_name]["objects"])
            else:
                sys.exit()

    def load_data(self, model_name):
        json_data = self.file_loader(model_name)
        self.data[model_name]["data"] = json_data
        return json_data

    def write_data_to_file(self, data, file_path):
        """
        Write data to data to json file on disk
        :param data: python dict of data to write
        :param file_path: path location and filename of file to write to

        """
        with open(file_path, "w") as outfile:
            json.dump(data, outfile)

    def read_api_from_file(self, file_path):
        """
        read api data from file
        :param file_path: file path
        :return: json data
        """

        with open(file_path) as f:
            json_data = json.load(f)
        return json_data

    def get_type_data_from_api(self, data_type=None):

        data = []

        logger.info("Getting {0} data".format(data_type))
        url = settings.TRADE_TARIFF_API["BASE_URL"].format(data_type)
        resp = requests.get(url)

        if resp.status_code == 200:
            data_type_json = resp.json()

            if data_type == "sections":
                data_type_ids = [item["id"] for item in data_type_json["data"]]
            elif data_type == "chapters":
                data_type_ids = [
                    item["attributes"]["goods_nomenclature_item_id"][:2]
                    for item in data_type_json["data"]
                ]

            data = self.get_item_data_from_api(data_type, data_type_ids)

        else:
            logger.debug("{0} returned a {1} error".format(url, resp.status_code))

        return data

    def get_item_data_from_api(self, data_type=None, item_ids=None):

        data = []
        child_data = []
        for item_id in item_ids:
            path = "{0}/{1}".format(
                "commodities" if data_type == "subheadings" else data_type, item_id
            )
            url = settings.TRADE_TARIFF_API["BASE_URL"].format(path)

            resp = requests.get(url)

            if resp.status_code == 200:
                item_json = resp.json()
                data.append(item_json)

                if data_type == "chapters":
                    child_data.extend(
                        [
                            item["attributes"]["goods_nomenclature_item_id"][:4]
                            for item in item_json["included"]
                            if item["type"] == "heading"
                        ]
                    )
                elif data_type == "headings":
                    child_data.extend(
                        [
                            item["attributes"]["goods_nomenclature_item_id"]
                            for item in item_json["included"]
                            if item["type"] == "commodity"
                        ]
                    )
            else:
                logger.debug("{0} returned a {1} error".format(url, resp.status_code))
        return data, child_data

    def build_import_data(self):

        """
        read json file from the filesystem that are serialized api calls
        generate import json files for section, chapters, headings, subheadings and commodities with correct
        parent child relationships and removing duplication
        """

        # read serialized api data from the filesystem
        sections = self.read_api_from_file(
            settings.IMPORT_DATA_PATH.format("downloaded/sections.json")
        )
        chapters = self.read_api_from_file(
            settings.IMPORT_DATA_PATH.format("downloaded/chapters.json")
        )
        headings = self.read_api_from_file(
            settings.IMPORT_DATA_PATH.format("downloaded/headings.json")
        )

        headings = self.remove_duplicate_headings_from_api(headings)

        # lists in which to collect instance data objects
        sections_data = []
        chapters_data = []
        headings_data = []
        sub_headings_data = []
        commodities_data = []

        if sections:

            for section in sections:
                sections_data.append(
                    {
                        "section_id": section["data"]["attributes"]["id"],
                        "roman_numeral": section["data"]["attributes"]["numeral"],
                        "title": section["data"]["attributes"]["title"],
                        "child_goods_nomenclature_sids": [
                            item["attributes"]["goods_nomenclature_sid"]
                            for item in section["included"]
                            if item["type"] == "chapter"
                        ],
                        "position": section["data"]["attributes"]["position"],
                    }
                )

        if chapters:

            for chapter in chapters:
                chapters_data.append(
                    {
                        "goods_nomenclature_item_id": chapter["data"]["attributes"][
                            "goods_nomenclature_item_id"
                        ],
                        "goods_nomenclature_sid": chapter["data"]["attributes"][
                            "goods_nomenclature_sid"
                        ],
                        "productline_suffix": "80",
                        "leaf": "0",
                        "parent_goods_nomenclature_item_id": "",
                        "parent_goods_nomenclature_sid": "-1",
                        "parent_productline_suffix": "",
                        "description": chapter["data"]["attributes"]["description"],
                        "number_indents": "0",
                    }
                )

                # extract all the heading objects with child items from the chapter's list of included children
                child_headings = [
                    item
                    for item in chapter["included"]
                    if item["type"] == "heading" and "relationships" in item.keys()
                ]
                heading_leaves = [
                    item
                    for item in chapter["included"]
                    if item["type"] == "heading" and item["attributes"]["leaf"] == True
                ]

                if child_headings:
                    for heading in child_headings:

                        headings_data.append(
                            {
                                "goods_nomenclature_item_id": heading["attributes"][
                                    "goods_nomenclature_item_id"
                                ],
                                "goods_nomenclature_sid": heading["attributes"][
                                    "goods_nomenclature_sid"
                                ],
                                "productline_suffix": heading["attributes"][
                                    "producline_suffix"
                                ],
                                "leaf": heading["attributes"]["leaf"],
                                "parent_goods_nomenclature_item_id": chapter["data"][
                                    "attributes"
                                ]["goods_nomenclature_item_id"],
                                "parent_goods_nomenclature_sid": chapter["data"][
                                    "attributes"
                                ]["goods_nomenclature_sid"],
                                "parent_productline_suffix": "",
                                "description": heading["attributes"]["description"],
                                "number_indents": "0",
                            }
                        )

                        if "relationships" in heading.keys():
                            children = heading["relationships"]["children"]["data"]

                        for leaf in heading_leaves:
                            if leaf["attributes"]["goods_nomenclature_sid"] in [
                                id for id in children
                            ]:
                                headings_data.append(
                                    {
                                        "goods_nomenclature_item_id": leaf[
                                            "attributes"
                                        ]["goods_nomenclature_item_id"],
                                        "goods_nomenclature_sid": leaf["attributes"][
                                            "goods_nomenclature_sid"
                                        ],
                                        "productline_suffix": leaf["attributes"][
                                            "producline_suffix"
                                        ],
                                        "leaf": leaf["attributes"]["leaf"],
                                        "parent_goods_nomenclature_item_id": heading[
                                            "data"
                                        ]["attributes"]["goods_nomenclature_item_id"],
                                        "parent_goods_nomenclature_sid": heading[
                                            "data"
                                        ]["attributes"]["goods_nomenclature_sid"],
                                        "parent_productline_suffix": "",
                                        "description": leaf["attributes"][
                                            "description"
                                        ],
                                        "number_indents": "0",
                                    }
                                )

                        if "relationships" in heading.keys():
                            for child in children:
                                for sub_heading in [
                                    item
                                    for item in headings
                                    if item["data"]["id"] == child["id"]
                                ]:
                                    leaves = [
                                        item
                                        for item in sub_heading["data"]["relationships"]
                                    ]
                                    sub_headings_data.append(
                                        {
                                            "goods_nomenclature_item_id": sub_heading[
                                                "data"
                                            ]["attributes"][
                                                "goods_nomenclature_item_id"
                                            ],
                                            "goods_nomenclature_sid": sub_heading[
                                                "data"
                                            ]["id"],
                                            "productline_suffix": "",
                                            "leaf": True
                                            if "commodities" in leaves
                                            else False,
                                            "parent_goods_nomenclature_item_id": heading[
                                                "attributes"
                                            ][
                                                "goods_nomenclature_item_id"
                                            ],
                                            "parent_goods_nomenclature_sid": heading[
                                                "attributes"
                                            ]["goods_nomenclature_sid"],
                                            "parent_productline_suffix": "",
                                            "description": sub_heading["data"][
                                                "attributes"
                                            ]["description"],
                                            "number_indents": "1",
                                        }
                                    )

        if headings:
            for heading in headings:
                heading_id = heading["data"]["id"]
                code = heading["data"]["attributes"]["goods_nomenclature_item_id"]

                sub_headings = [
                    item
                    for item in heading["included"]
                    if item["type"] == "commodity"
                    and item["attributes"]["leaf"] is False
                ]

                for sub_heading in sub_headings:
                    parent_sid = sub_heading["attributes"]["parent_sid"]

                    sub_headings_data.append(
                        {
                            "goods_nomenclature_item_id": sub_heading["attributes"][
                                "goods_nomenclature_item_id"
                            ],
                            "goods_nomenclature_sid": sub_heading["attributes"][
                                "goods_nomenclature_sid"
                            ],
                            "productline_suffix": sub_heading["attributes"][
                                "producline_suffix"
                            ],
                            "leaf": sub_heading["attributes"]["leaf"],
                            "parent_goods_nomenclature_item_id": code,
                            "parent_goods_nomenclature_sid": parent_sid
                            if parent_sid is not None
                            else heading_id,
                            "parent_productline_suffix": "",
                            "description": sub_heading["attributes"]["description"],
                            "number_indents": sub_heading["attributes"][
                                "number_indents"
                            ],
                        }
                    )

                commodities = [
                    item
                    for item in heading["included"]
                    if item["type"] == "commodity"
                    and item["attributes"]["leaf"] is True
                ]

                commodity_lookup = {
                    item["attributes"]["goods_nomenclature_sid"]: item["attributes"][
                        "goods_nomenclature_item_id"
                    ]
                    for item in heading["included"]
                    if item["type"] == "commodity"
                }

                for commodity in commodities:

                    parent_sid = commodity["attributes"]["parent_sid"]

                    commodities_data.append(
                        {
                            "goods_nomenclature_item_id": commodity["attributes"][
                                "goods_nomenclature_item_id"
                            ],
                            "goods_nomenclature_sid": commodity["attributes"][
                                "goods_nomenclature_sid"
                            ],
                            "productline_suffix": commodity["attributes"][
                                "producline_suffix"
                            ],
                            "leaf": commodity["attributes"]["leaf"],
                            "parent_goods_nomenclature_item_id": commodity_lookup[
                                int(parent_sid)
                            ]
                            if parent_sid is not None
                            else code,
                            "parent_goods_nomenclature_sid": parent_sid
                            if parent_sid is not None
                            else heading_id,
                            "parent_productline_suffix": "",
                            "description": commodity["attributes"]["description"],
                            "number_indents": commodity["attributes"]["number_indents"],
                        }
                    )

        # remove any duplicates
        headings_data = [dict(t) for t in {tuple(d.items()) for d in headings_data}]
        sub_headings_data = [
            dict(t) for t in {tuple(d.items()) for d in sub_headings_data}
        ]
        commodities_data = [
            dict(t) for t in {tuple(d.items()) for d in commodities_data}
        ]

        # serialize to filesystem
        self.write_data_to_file(
            sections_data, settings.IMPORT_DATA_PATH.format("prepared/sections.json")
        )
        self.write_data_to_file(
            chapters_data, settings.IMPORT_DATA_PATH.format("prepared/chapters.json")
        )
        self.write_data_to_file(
            headings_data, settings.IMPORT_DATA_PATH.format("prepared/headings.json")
        )
        self.write_data_to_file(
            sub_headings_data,
            settings.IMPORT_DATA_PATH.format("prepared/sub_headings.json"),
        )
        self.write_data_to_file(
            commodities_data,
            settings.IMPORT_DATA_PATH.format("prepared/commodities.json"),
        )

    @staticmethod
    def remove_duplicate_headings_from_api(json_obj):
        """
        remove duplicate headings from the downloaded api data
        :param json_obj: downloaded list of headings
        :return: deduped list of headings
        """
        seen = []
        new_json_obj = []
        for heading in json_obj:
            if heading["data"]["attributes"]["goods_nomenclature_item_id"] not in seen:
                new_json_obj.append(heading)
                seen.append(heading["data"]["attributes"]["goods_nomenclature_item_id"])
        return new_json_obj

    def save_trade_tariff_service_api_data_json_to_file(self):
        """
        check for previously downloaded content and archive
        Get Sections, Chapters and Headings api data from the trade tariff service api and serialize it locally to disk
        This will be used by `build_import_data` to create the json files that will be used to create the
        main hierarchy structural elements
        :return:
        """
        logger.info(
            "This will retrieve the json data for Sections, Chapters and Headings from the trade tariff api"
            " service and save the json files to the filesystem."
        )
        download_dir = settings.IMPORT_DATA_PATH.format("downloaded")
        previous_dir = "{0}/previous".format(download_dir)

        # try:
        #     os.mkdir(previous_dir, 777)
        # except FileExistsError as exception:
        #     logger.info("{0}".format(exception.args))

        previous_files = [
            f
            for f in os.listdir(download_dir)
            if os.path.isfile(os.path.join(download_dir, f))
        ]

        for f in previous_files:
            os.rename(os.path.join(download_dir, f), os.path.join(previous_dir, f))

        data_type = "sections"
        sections, _ = self.get_type_data_from_api(data_type=data_type)
        logger.info("Writing {0} data".format(data_type))
        self.write_data_to_file(
            sections,
            settings.IMPORT_DATA_PATH.format("downloaded/{0}.json".format(data_type)),
        )

        data_type = "chapters"
        chapters, heading_ids = self.get_type_data_from_api(data_type=data_type)
        logger.info("Writing {0} data".format(data_type))
        self.write_data_to_file(
            chapters,
            settings.IMPORT_DATA_PATH.format("downloaded/{0}.json".format(data_type)),
        )

        data_type = "headings"
        headings, commodity_ids = self.get_item_data_from_api(
            data_type=data_type, item_ids=heading_ids
        )
        logger.info("Writing {0} data".format(data_type))
        self.write_data_to_file(
            headings,
            settings.IMPORT_DATA_PATH.format("downloaded/{0}.json".format(data_type)),
        )

    def lookup_parent(self, parent_model, child_parent_code):
        """
        find a parent instance if the parent is a Section
        - by matching a child's `goods_nomenclature_sid` in a Sections list of `child_goods_nomenclature_sids`
        find a parent instance if the parent is a Chapter, Heading or SubHeading
        - by matching the childs's `parent_goods_nomenclature_sid` to the parents's `goods_nomenclature_sid'
        :param model: Parent model
        :param code: parent code from child data
        :return:
        """

        for item in self.data[parent_model.__name__]["data"]:
            if parent_model is Section:
                if int(child_parent_code) in item["child_goods_nomenclature_sids"]:
                    return Section.objects.get(section_id=int(item["section_id"]))
            else:
                try:
                    return parent_model.objects.get(
                        goods_nomenclature_sid=child_parent_code
                    )
                except ObjectDoesNotExist as exception:
                    logger.debug("{0} lookup parent:{1} ".format(item, exception.args))
                    return None

    def build_search_data(self):
        file_list = [
            hierarchy_model_map[item]["file_name"]
            for item in hierarchy_model_map.keys()
            if item != "Section"
        ]
        data = []
        for item in file_list:
            data.extend(self.load_json_file(settings.IMPORT_DATA_PATH.format(item)))
            # self.convert_json_to_csv(file_name=item[0], json_file=item[1])
        data = sorted(data, key=lambda i: i["goods_nomenclature_item_id"])

        self.convert_json_to_csv(data=data)

    def convert_json_to_csv(self, data=None):
        # get filename from filepath

        csv_file_path = settings.SEARCH_DATA_PATH.format(
            "commodities/hierarchy_subheading_all.csv"
        )
        csv_data = csv.writer(open(csv_file_path, "a", newline=""))
        col_headings = [
            "Code",
            "Col1",
            "Col2",
            "Col3",
            "Col4",
            "Col5",
            "Col6",
            "Col7",
            "Col8",
        ]
        csv_data.writerow(col_headings)

        for item in data:
            csv_data.writerow(
                [
                    item["goods_nomenclature_item_id"],
                    item["goods_nomenclature_sid"],
                    item["productline_suffix"],
                    item["leaf"],
                    item["parent_goods_nomenclature_item_id"],
                    item["parent_goods_nomenclature_sid"],
                    item["parent_productline_suffix"],
                    item["description"],
                    item["number_indents"],
                ]
            )

    def load_json_file(self, file_path):
        with open(file_path) as f:
            json_data = json.load(f)
        return json_data

    @staticmethod
    def process_orphaned_subheadings():
        """
        this method is to be run after data scanner has created all hierarchy items in the database
        the method finds parents for all subheading items and updates the database accordingly
        """

        logger.info("Processing orphaned subheading parents")
        subheadings = SubHeading.objects.filter(
            heading_id=None, parent_subheading_id=None
        )

        count = 0
        for subheading in subheadings:
            parent_sid = subheading.parent_goods_nomenclature_sid
            try:
                parent = SubHeading.objects.get(goods_nomenclature_sid=parent_sid)
                subheading.parent_subheading_id = parent.pk
                subheading.save()
            except ObjectDoesNotExist as exception:
                logger.info(
                    "{0} has no parent SubHeading {1}".format(
                        subheading, exception.args
                    )
                )
                try:
                    parent = Heading.objects.get(goods_nomenclature_sid=parent_sid)
                    subheading.heading_id = parent.pk
                    subheading.save()
                except ObjectDoesNotExist as exception:
                    logger.info(
                        "{0} has no parent Heading {1}".format(
                            subheading, exception.args
                        )
                    )
            count = count + 1
        return count

    @staticmethod
    def process_orphaned_commodities():
        """
        this method is to be run after data scanner has created all hierarchy items in the database
        the method finds parents for all commodty items and updates the database accordingly

        """

        logger.info("Processing orphaned commodity parents")
        commodities = Commodity.objects.filter(
            heading_id=None, parent_subheading_id=None
        )

        for commodity in commodities:
            parent_sid = commodity.parent_goods_nomenclature_sid

            try:

                if parent_sid is None:
                    subheading = SubHeading.objects.get(
                        commodity_code=commodity.parent_goods_nomenclature_item_id
                    )
                    parent_sid = subheading.goods_nomenclature_sid

                parent = SubHeading.objects.get(goods_nomenclature_sid=parent_sid)
                commodity.parent_subheading_id = parent.pk

            except ObjectDoesNotExist as exception:
                logger.debug(
                    "Commodity {0} has no subheading parent parant {1}".format(
                        commodity, exception.args
                    )
                )

                if parent_sid is None:
                    heading = Heading.objects.get(
                        heading_code=commodity.parent_goods_nomenclature_item_id
                    )
                    parent_sid = heading.goods_nomenclature_sid

                parent = Heading.objects.get(goods_nomenclature_sid=parent_sid)
                commodity.heading_id = parent.pk

            commodity.save()

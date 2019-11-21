import json
import logging
from pathlib import Path
from pprint import pprint

import pandas
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from commodities.models import Commodity
from hierarchy.models import Heading, SubHeading, Section, Chapter

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


def data_loader(file_path):

    """
    :param file_path:
    :return:
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


class SearchKeywordsImporter:
    def __init__(self):
        self.data = {}
        self.documents = None
        self.app_label = __package__.rsplit(".", 1)[-1]
        self.data_path = settings.SEARCH_DATA_PATH
        self.section_codes = [section.section_id for section in Section.objects.all()]
        self.chapter_codes = [chapter.chapter_code for chapter in Chapter.objects.all()]
        self.heading_codes = [heading.heading_code for heading in Heading.objects.all()]
        self.subheading_codes = [
            subheading.commodity_code for subheading in SubHeading.objects.all()
        ]
        self.commodity_codes = [
            commodity.commodity_code for commodity in Commodity.objects.all()
        ]

    def load(self, file_path):
        f = self.data_path.format(file_path)

        data = json.loads(data_loader(f).to_json(orient="records"))

        instance_data = {}
        for item in data:
            if len(str(item["Code"])) == 9:
                commodity_code = "0" + str(item["Code"])
            else:
                commodity_code = str(item["Code"])

            instance_data[commodity_code] = {}

            if "keywords" in instance_data[commodity_code].keys() and isinstance(
                instance_data[commodity_code]["keywords"], list
            ):
                instance_data[commodity_code]["keywords"].append(item["final_category"])
                instance_data[commodity_code]["ranking_score"] = item["ranking_score"]
            else:
                instance_data[commodity_code]["keywords"] = [item["final_category"]]
                instance_data[commodity_code]["ranking_score"] = item["ranking_score"]

        for commodity_code in instance_data.keys():

            instance = {commodity_code: instance_data[commodity_code]}
            if commodity_code in self.chapter_codes:

                if "Chapter" in self.data.keys() and isinstance(
                    self.data["Chapter"], list
                ):
                    self.data["Chapter"].append(instance)
                else:
                    self.data["Chapter"] = [instance]

            if commodity_code in self.heading_codes:
                if "Heading" in self.data.keys() and isinstance(
                    self.data["Heading"], list
                ):
                    self.data["Heading"].append(instance)
                else:
                    self.data["Heading"] = [instance]

            if commodity_code in self.subheading_codes:
                if "SubHeading" in self.data.keys() and isinstance(
                    self.data["SubHeading"], list
                ):
                    self.data["SubHeading"].append(instance)
                else:
                    self.data["SubHeading"] = [instance]

            if commodity_code in self.commodity_codes:
                if "Commodity" in self.data.keys() and isinstance(
                    self.data["Commodity"], list
                ):
                    self.data["Commodity"].append(instance)
                else:
                    self.data["Commodity"] = [instance]

    def process(self):

        multiples_found = []
        not_found = []

        for model_name in self.data.keys():
            for item in self.data[model_name]:
                field_data = {}

                commodity_code = next(iter(item.keys()))
                field_data["keywords"] = " ".join(item[commodity_code]["keywords"])
                field_data["ranking"] = item[commodity_code]["ranking_score"]

                app_label = "commodities" if model_name == "Commodity" else "hierarchy"
                model = apps.get_model(app_label=app_label, model_name=model_name)
                obj = created = None
                if model_name == "Chapter":
                    obj, created = model.objects.update_or_create(
                        chapter_code=commodity_code, defaults=field_data
                    )
                elif model_name == "Heading":
                    try:
                        obj, created = model.objects.update_or_create(
                            heading_code=commodity_code, defaults=field_data
                        )
                    except ObjectDoesNotExist as err:
                        not_found.append((model_name, commodity_code))
                        logger.debug(
                            "update or create {0} {1}".format(err.args, commodity_code)
                        )
                    except MultipleObjectsReturned as m_err:
                        multiples_found.append((model_name, commodity_code))
                        logger.debug(
                            "multiple found {0} {1}".format(m_err.args, commodity_code)
                        )
                    except Exception as ex:
                        logger.debug(ex.args)
                else:
                    try:
                        obj, created = model.objects.update_or_create(
                            commodity_code=commodity_code, defaults=field_data
                        )
                    except ObjectDoesNotExist as err:
                        not_found.append((model_name, commodity_code))
                        logger.debug(
                            "update or create {0} {1}".format(err.args, commodity_code)
                        )
                    except MultipleObjectsReturned as m_err:
                        multiples_found.append((model_name, commodity_code))
                        logger.debug(
                            "multiple found {0} {1}".format(m_err.args, commodity_code)
                        )
                    except Exception as ex:
                        logger.debug(ex.args)

                if not isinstance(obj, Commodity):
                    try:
                        if obj.get_hierarchy_children_count() > 0:
                            obj.leaf = False
                        else:
                            obj.leaf = True
                        obj.save()
                    except AttributeError as ae:
                        logger.debug(ae.args)

                if not created:
                    logger.info("{0} instance updated".format(obj))
                else:
                    logger.info("{0} instance created".format(obj))

        logger.info("Multiples Found: {0}".format(multiples_found))
        logger.info("Not founds: {0}".format(not_found))

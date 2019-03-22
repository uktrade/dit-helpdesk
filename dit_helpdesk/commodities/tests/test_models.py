import json

from django.apps import apps
from django.conf import settings
from django.test import TestCase
from commodities.models import Commodity


COMMODITY_DATA = settings.BASE_DIR+"/commodities/tests/commodity_0101210000.json"
COMMODITY_STRUCTURE = settings.BASE_DIR+"/commodities/tests/structure_0101210000.json"
SUBHEADING_STRUCTURE = settings.BASE_DIR+"/hierarchy/tests/subheading_0101210000_structure.json"
HEADING_STRUCTURE = settings.BASE_DIR+"/hierarchy/tests/heading_0101000000_structure.json"


class TestCommodityModels(TestCase):

    def get_data(self, file_path):

        with open(file_path) as f:
            json_data = json.load(f)
        return json_data

    def create_instance(self, data, app_name, model_name):

        model = apps.get_model(app_label=app_name, model_name=model_name)
        instance = model(**data)
        return instance

    def setUp(self):

        self.heading = self.create_instance(self.get_data(HEADING_STRUCTURE), 'hierarchy', 'Heading')

        self.subheading = self.create_instance(self.get_data(SUBHEADING_STRUCTURE), 'hierarchy', 'SubHeading')
        self.subheading.heading_id = self.heading.id
        self.subheading.save()

        self.commodity = self.create_instance(self.get_data(COMMODITY_STRUCTURE), 'commodities', 'Commodity')
        self.commodity.subheading_id = self.subheading.id
        self.commodity.save()

    def test_get_heading(self):

        self.assertEquals(
            "Live horses, asses, mules and hinnies",
            self.commodity.get_heading()
        )

    def test_tts_title(self):
        pass

    def test_tt_heading_description(self):
        pass

    def test_heading_obj(self):
        pass

    def test_commodity_code_splt(self):
        pass

    def test_get_absolute_url(self):
        pass

    def test_hierarchy_key(self):
        pass





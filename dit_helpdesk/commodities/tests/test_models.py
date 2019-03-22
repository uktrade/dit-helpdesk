from django.test import TestCase
from django.test import reverse

from commodities.models import Commodity

commodity_struct_data = """{
		"goods_nomenclature_item_id": "0101210000",
		"goods_nomenclature_sid": "93796",
		"productline_suffix": "80",
		"leaf": "1",
		"parent_goods_nomenclature_item_id": "0101210000",
		"parent_goods_nomenclature_sid": "93797",
		"parent_productline_suffix": "10",
		"description": "Pure-bred breeding animals",
		"number_indents": "2"
	}"""

subheading_struct_data = """{
		"goods_nomenclature_item_id": "0101210000",
		"goods_nomenclature_sid": "93797",
		"productline_suffix": "10",
		"leaf": "0",
		"parent_goods_nomenclature_item_id": "0101000000",
		"parent_goods_nomenclature_sid": "27624",
		"parent_productline_suffix": "80",
		"description": "Horses",
		"number_indents": "1"
	}"""

heading_struct_data = """{
		"goods_nomenclature_item_id": "0101000000",
		"goods_nomenclature_sid": "27624",
		"productline_suffix": "80",
		"leaf": "0",
		"parent_goods_nomenclature_item_id": "0100000000",
		"parent_goods_nomenclature_sid": "27623",
		"parent_productline_suffix": "80",
		"description": "Live horses, asses, mules and hinnies",
		"number_indents": "0"
	}"""

class TestCommoditiesModels(TestCase):

    def test_get_heading(self):

        data = {
            "commodity_code": "",
            "goods_nomenclature_sid": "",
            "productline_suffix": "",
            "parent_goods_nomenclature_item_id": "",
            "parent_goods_nomenclature_sid": "",
            "parent_productline_suffix": "",
            "description": "",
            "number_indents": 0,
            "tts_json": "",
            "tts_heading_json": "",
            "tts_is_leaf": False,
            "heading": None,
            "parent_subheading": None,
            "last_updated": None
        }
        commodity = Commodity()


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





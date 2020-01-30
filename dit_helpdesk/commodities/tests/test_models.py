import datetime
import logging
import json

from django.conf import settings
from django.test import TestCase
from django.urls import NoReverseMatch
from mixer.backend.django import mixer
from commodities.models import Commodity
from hierarchy.models import SubHeading, Heading, Chapter, Section
from trade_tariff_service.tts_api import CommodityJson

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


def get_data(file_path):
    with open(file_path) as f:
        json_data = json.load(f)
    return json_data


class CommodityTestCase(TestCase):

    """
    Test Commodities Models
    """

    def setUp(self):
        self.section = mixer.blend(Section, section_id=1)
        self.chapter = mixer.blend(
            Chapter, chapter_code="0100000000", section=self.section
        )

        self.heading = mixer.blend(
            Heading, heading_code="0101000000", chapter=self.chapter
        )

        self.subheading = mixer.blend(
            SubHeading, commodity_code="0101210000", heading=self.heading
        )

        self.commodity = mixer.blend(
            Commodity,
            commodity_code="0101210000",
            tts_json=json.dumps(get_data(settings.COMMODITY_STRUCTURE)),
            parent_subheading=self.subheading,
            goods_nomenclature_sid=12345,
        )

    def test_str(self):
        self.assertEquals(
            str(self.commodity), "Commodity {0}".format(self.commodity.commodity_code)
        )

    def test_hierarchy_key(self):
        self.assertEquals(
            self.commodity.hierarchy_key, "commodity-{0}".format(self.commodity.pk)
        )

    def test_get_absolute_url_with_lowercase_country_code(self):
        self.assertEquals(
            self.commodity.get_absolute_url(country_code="au"),
            "/country/au/commodity/0101210000/12345",
        )

    def test_get_absolute_url_without_country_code(self):
        self.assertRaises(NoReverseMatch, lambda: self.commodity.get_absolute_url())

    def test_get_absolute_url_with_uppercased_country_code(self):
        self.assertEquals(
            self.commodity.get_absolute_url(country_code="AU"),
            "/country/au/commodity/{0}/12345".format(self.commodity.commodity_code),
        )

    def test_commodity_code_split(self):
        self.assertEquals(
            self.commodity.commodity_code_split, ["0101", "21", "00", "00"]
        )

    def test_tts_json_is_a_string_representing_a_json_object(self):
        self.assertTrue(isinstance(self.commodity.tts_json, str))

    def test_tts_json_is_the_correct_data(self):
        self.assertEquals(
            self.commodity.tts_json, json.dumps(get_data(settings.COMMODITY_STRUCTURE))
        )

    def test_tts_obj_is_a_CommodityJson_object(self):
        self.assertTrue(isinstance(self.commodity.tts_obj, CommodityJson))

    def test_get_heading_is_type_heading_with_code_0101000000(self):
        self.assertTrue(isinstance(self.commodity.get_heading(), Heading))
        self.assertEquals(self.commodity.get_heading().heading_code, "0101000000")

    def test_get_path_returns_list(self):
        self.assertTrue(isinstance(self.commodity.get_path(), list))

    def test_get_path_with_lelve_less_than_length_of_tree(self):
        tree = [
            [self.section],
            [self.chapter],
            [self.heading],
            [self.subheading],
            [self.commodity],
        ]
        level = 2
        parent = self.heading
        logger.debug(self.commodity.get_path(parent=parent, tree=tree, level=level))
        self.assertTrue(self.commodity.get_path(parent=parent, tree=tree, level=level))

    def test_get_path_returns_list_with_no_parent_subheading(self):
        section = mixer.blend(Section, section_id=10)

        chapter = mixer.blend(
            Chapter,
            chapter_code="4700000000",
            section=section,
            goods_nomenclature_sid=12345,
        )

        heading = mixer.blend(
            Heading,
            heading_code="4702000000",
            chapter=chapter,
            goods_nomenclature_sid=12345,
        )

        commodity = mixer.blend(
            Commodity,
            commodity_code="4702000000",
            heading=heading,
            goods_nomenclature_sid=12345,
        )

        self.assertTrue(
            "subheading"
            not in [
                "".join([item._meta.model_name for item in item_list])
                for item_list in commodity.get_path()
            ]
        )

    def test_get_path_returns_list_with_multiple_parent_subheadings(self):
        section = mixer.blend(Section, section_id=10)

        chapter = mixer.blend(Chapter, chapter_code="4700000000", section=section)

        heading = mixer.blend(
            Heading,
            heading_code="4704000000",
            chapter=chapter,
            goods_nomenclature_sid=12345,
        )
        subheading = mixer.blend(
            SubHeading,
            commodity_code="4704000000",
            heading=heading,
            goods_nomenclature_sid=12345,
        )
        sub_subheading = mixer.blend(
            SubHeading,
            commodity_code="4704110000",
            parent_subheading=subheading,
            goods_nomenclature_sid=12345,
        )
        commodity = mixer.blend(
            Commodity,
            commodity_code="4702000000",
            parent_subheading=sub_subheading,
            goods_nomenclature_sid=12345,
        )
        self.assertTrue(
            "4704110000"
            and "4704000000"
            in [
                "".join(
                    [
                        item.commodity_code
                        for item in item_list
                        if item._meta.model_name == "subheading"
                    ]
                )
                for item_list in commodity.get_path()
            ]
        )

    def test_get_path_returns_list_contains_commodity_item(self):
        self.assertTrue(
            "commodity"
            in [
                "".join([item._meta.model_name for item in item_list])
                for item_list in self.commodity.get_path()
            ]
        )

    def test_get_path_returns_list_contains_subheading_item(self):
        self.assertTrue(
            "subheading"
            in [
                "".join([item._meta.model_name for item in item_list])
                for item_list in self.commodity.get_path()
            ]
        )

    def test_get_path_returns_list_contains_heading_item(self):
        self.assertTrue(
            "heading"
            in [
                "".join([item._meta.model_name for item in item_list])
                for item_list in self.commodity.get_path()
            ]
        )

    def test_get_path_returns_list_contains_chapter_item(self):
        self.assertTrue(
            "chapter"
            in [
                "".join([item._meta.model_name for item in item_list])
                for item_list in self.commodity.get_path()
            ]
        )

    def test_get_path_returns_list_contains_section_item(self):
        self.assertTrue(
            "section"
            in [
                "".join([item._meta.model_name for item in item_list])
                for item_list in self.commodity.get_path()
            ]
        )

    def test_append_path_children(self):
        self.assertTrue(self.commodity._append_path_children)

    def test_commodity_update_content(self):
        self.commodity.update_content()
        test_time = datetime.datetime.now(datetime.timezone.utc)
        check = self.commodity.last_updated - test_time
        self.assertAlmostEqual(
            self.commodity.last_updated > test_time
            and check < datetime.timedelta(minutes=2),
            False,
        )

    def test_heading_leaf_update_content(self):
        commodity = mixer.blend(Commodity, commodity_code="0510000000")

        commodity.update_content()
        content = json.loads(commodity.tts_json)
        self.assertEqual(content["goods_nomenclature_item_id"], "0510000000")

        test_time = datetime.datetime.now(datetime.timezone.utc)
        check = self.commodity.last_updated - test_time
        self.assertAlmostEqual(
            self.commodity.last_updated > test_time
            and check < datetime.timedelta(minutes=2),
            False,
        )

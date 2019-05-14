import logging
import json
import os
import re

from django.apps import apps
from django.conf import settings
from django.test import TestCase
from django.urls import NoReverseMatch
from mixer.backend.django import mixer
from commodities.models import Commodity
from hierarchy.models import SubHeading, Heading, Chapter, Section
from trade_tariff_service.tts_api import CommodityJson, CommodityHeadingJson

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class CommodityTestCase(TestCase):

    """
    Test Commodities Models
    """

    def setUp(self):
        self.section = mixer.blend(
            Section,
            section_id=1
        )
        self.chapter = mixer.blend(
            Chapter,
            chapter_code="0100000000",
            section=self.section
        )

        self.heading = mixer.blend(
            Heading,
            heading_code="0101000000",
            chapter=self.chapter
        )

        self.subheading = mixer.blend(
            SubHeading,
            commodity_code="0101210000",
            heading=self.heading

        )
        self.commodity = mixer.blend(
            Commodity,
            commodity_code="0101210000",
            tts_json="{}",
            tts_heading_json="{}",
            parent_subheading=self.subheading
        )

    def test_str(self):
        self.assertEquals(str(self.commodity), "Commodity {0}".format(self.commodity.commodity_code))

    def test_hierarchy_key(self):
        self.assertEquals(self.commodity.hierarchy_key, "commodity-{0}".format(self.commodity.pk))

    def test_get_absolute_url_with_lowercase_country_code(self):
        self.assertEquals(self.commodity.get_absolute_url(country_code="au"), "/country/au/commodity/0101210000")

    def test_get_absolute_url_without_country_code(self):
        self.assertRaises(NoReverseMatch, lambda: self.commodity.get_absolute_url())

    def test_get_absolute_url_with_uppercased_country_code(self):
        self.assertEquals(self.commodity.get_absolute_url(country_code="AU"),
                          "/country/au/commodity/{0}".format(self.commodity.commodity_code))

    def test_commodity_code_split(self):
        self.assertEquals(self.commodity.commodity_code_split, ['010121', '00', '00'])

    def test_tts_json_is_a_string_representing_a_json_object(self):
        self.assertTrue(isinstance(self.commodity.tts_json, str))
        self.assertEquals(self.commodity.tts_json, "{}")

    def test_tts_obj_is_and_empty_CommodityJson_object(self):
        self.assertTrue(isinstance(self.commodity.tts_obj, CommodityJson))
        self.assertFalse(self.commodity.tts_obj.di)

    def test_heading_tts_json_is_a_string_representing_a_json_object(self):
        # TODO: if not used remove field from Commodity Model
        self.assertTrue(isinstance(self.commodity.tts_heading_json, str))
        self.assertEquals(self.commodity.tts_heading_json, "{}")

    def test_tts_obj_is_and_empty_CommodityHeadingJson_object(self):
        # TODO: if not used remove method from Commodity model
        self.assertTrue(isinstance(self.commodity.tts_heading_obj, CommodityHeadingJson))
        self.assertFalse(self.commodity.tts_heading_obj.di)

    def test_tts_title(self):
        # TODO: if not used remove method from Commodity model
        self.assertEquals(self.commodity.tts_title, self.commodity.description)

    def test_heading_description(self):
        # TODO: if not used remove method from Commodity model
        self.assertEquals(self.commodity.tts_heading_description, self.commodity.description)

    def test_get_heading_is_type_heading_with_code_0101000000(self):
        self.assertTrue(isinstance(self.commodity.get_heading(), Heading))
        self.assertEquals(self.commodity.get_heading().heading_code, "0101000000")

    def test_get_path_returns_list(self):
        self.assertTrue(isinstance(self.commodity.get_path(), list))

    def test_get_path_with_lelve_less_than_length_of_tree(self):
        tree = [[self.section], [self.chapter], [self.heading], [self.subheading], [self.commodity]]
        level = 2
        parent = self.heading
        logger.debug(self.commodity.get_path(parent=parent, tree=tree, level=level))
        self.assertTrue(self.commodity.get_path(parent=parent, tree=tree, level=level))

    def test_get_path_returns_list_with_no_parent_subheading(self):
        section = mixer.blend(
            Section,
            section_id=10
        )

        chapter = mixer.blend(
            Chapter,
            chapter_code="4700000000",
            section=section

        )

        heading = mixer.blend(
            Heading,
            heading_code="4702000000",
            chapter=chapter
        )

        commodity = mixer.blend(
            Commodity,
            commodity_code="4702000000",
            heading=heading
        )

        self.assertTrue("subheading" not in [''.join([item._meta.model_name for item in item_list])
                                             for item_list in commodity.get_path()])

    def test_get_path_returns_list_with_multiple_parent_subheadings(self):
        section = mixer.blend(
            Section,
            section_id=10
        )

        chapter = mixer.blend(
            Chapter,
            chapter_code="4700000000",
            section=section

        )

        heading = mixer.blend(
            Heading,
            heading_code="4704000000",
            chapter=chapter
        )
        subheading = mixer.blend(
            SubHeading,
            commodity_code="4704000000",
            heading=heading
        )
        sub_subheading = mixer.blend(
            SubHeading,
            commodity_code="4704110000",
            parent_subheading=subheading
        )
        commodity = mixer.blend(
            Commodity,
            commodity_code="4702000000",
            parent_subheading=sub_subheading
        )
        self.assertTrue("4704110000" and "4704000000" in [''.join([item.commodity_code for item in item_list
                                                                   if item._meta.model_name == 'subheading'])
                                                          for item_list in commodity.get_path()])

    def test_get_path_returns_list_contains_commodity_item(self):
        self.assertTrue("commodity" in [''.join([item._meta.model_name for item in item_list])
                                        for item_list in self.commodity.get_path()])

    def test_get_path_returns_list_contains_subheading_item(self):
        self.assertTrue("subheading" in [''.join([item._meta.model_name for item in item_list])
                                         for item_list in self.commodity.get_path()])

    def test_get_path_returns_list_contains_heading_item(self):
        self.assertTrue("heading" in [''.join([item._meta.model_name for item in item_list])
                                      for item_list in self.commodity.get_path()])

    def test_get_path_returns_list_contains_chapter_item(self):
        self.assertTrue("chapter" in [''.join([item._meta.model_name for item in item_list])
                                      for item_list in self.commodity.get_path()])

    def test_get_path_returns_list_contains_section_item(self):
        self.assertTrue("section" in [''.join([item._meta.model_name for item in item_list])
                                      for item_list in self.commodity.get_path()])

    def test_append_path_children(self):
        self.assertTrue(self.commodity._append_path_children)

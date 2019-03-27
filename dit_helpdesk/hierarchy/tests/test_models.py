import json
import os

from django.apps import apps
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from commodities.models import Commodity
from hierarchy.models import SubHeading, Heading, Section, Chapter
from trade_tariff_service.tts_api import CommodityJson, CommodityHeadingJson, ChapterJson, HeadingJson, SectionJson

TEST_COMMODITY_CODE = "0101210000"
TEST_SUBHEADING_CODE = "0101210000"
TEST_HEADING_CODE = "0101000000"
TEST_HEADING_CODE_SHORT = "0101"
TEST_CHAPTER_CODE = "0100000000"
TEST_SECTION_ID = "1"
TEST_COUNTRY_CODE = "AU"
TEST_COUNTRY_NAME = "Australia"
TEST_HEADING_DESCRIPTION = "Live horses, asses, mules and hinnies"
TEST_SUBHEADING_DESCRIPTION = "Horses"
TEST_SECTION_DESCRIPTION = "Live animals; animal products"
TEST_CHAPTER_DESCRIPTION = "LIVE ANIMALS"

COMMODITY_DATA = settings.BASE_DIR+"/commodities/tests/commodity_{0}.json".format(TEST_COMMODITY_CODE)
COMMODITY_STRUCTURE = settings.BASE_DIR+"/commodities/tests/structure_{0}.json".format(TEST_COMMODITY_CODE)
SUBHEADING_STRUCTURE = settings.BASE_DIR+"/hierarchy/tests/subheading_{0}_structure.json".format(TEST_SUBHEADING_CODE)
HEADING_STRUCTURE = settings.BASE_DIR+"/hierarchy/tests/heading_{0}_structure.json".format(TEST_HEADING_CODE)
CHAPTER_STRUCTURE = settings.BASE_DIR+"/hierarchy/tests/chapter_{0}_structure.json".format(TEST_CHAPTER_CODE)
SECTION_STRUCTURE = settings.BASE_DIR+"/hierarchy/tests/section_{}_structure.json".format(TEST_SECTION_ID)


class HierarchyModelsTestCase(TestCase):

    def get_data(self, file_path):

        with open(file_path) as f:
            json_data = json.load(f)
        return json_data

    def create_instance(self, data, app_name, model_name):

        model = apps.get_model(app_label=app_name, model_name=model_name)
        instance = model(**data)
        instance.save()
        return instance

    def setUp(self):
        """
        To test fully test a commodity we need to load a parent subheading and its parent heading and save the
        relationships between the three model instances
        :return:
        """
        self.section = self.create_instance(self.get_data(SECTION_STRUCTURE), 'hierarchy', 'Section')

        self.chapter = self.create_instance(self.get_data(CHAPTER_STRUCTURE), 'hierarchy', 'Chapter')
        self.chapter.section_id = self.chapter.pk
        self.chapter.save()

        self.heading = self.create_instance(self.get_data(HEADING_STRUCTURE), 'hierarchy', 'Heading')
        self.heading.chapter_id = self.chapter.id
        self.heading.save()

        self.subheading = self.create_instance(self.get_data(SUBHEADING_STRUCTURE), 'hierarchy', 'SubHeading')
        self.subheading.heading_id = self.heading.id
        self.subheading.save()

        self.commodity = self.create_instance(self.get_data(COMMODITY_STRUCTURE), 'commodities', 'Commodity')
        self.commodity.parent_subheading_id = self.subheading.id
        self.commodity.tts_json = json.dumps(self.get_data(COMMODITY_DATA))

        self.commodity.save()

    def test_section_instance_exists(self):
        self.assertTrue(Section.objects.get(section_id=TEST_SECTION_ID))

    def test_self_section_is_and_instance_of_Section(self):
        self.assertTrue(isinstance(self.section, Section))

    def test_section_hierarchy_key_is_correct(self):
        self.assertEqual(self.section.hierarchy_key, "section-{0}".format(self.section.pk))

    def test_section_has_the_correct_hierarchy_url(self):
        self.assertEqual(self.section.get_hierarchy_url(TEST_COUNTRY_CODE),
                         "/search/country/au/hierarchy/section-{0}".format(self.section.pk))

    def test_section_has_hierarchy_children(self):
        self.assertTrue(len(self.section.get_hierarchy_children()) > 0)

    def test_section_has_child_chapters(self):
        self.assertTrue(self.section.chapter_range_str is not None)

    def test_section_has_child_chapters_str_is_a_string(self):
        # TODO: asdd more chapters to test correct string is returned
        self.assertTrue(isinstance(self.section.chapter_range_str, str))

    def test_section_tts_title_is_correct(self):
        self.assertEqual(self.section.title, TEST_SECTION_DESCRIPTION)

    def test_section_has_tts_obj(self):
        # self.assertTrue(isinstance(self.section.tts_obj, SectionJson))
        self.assertTrue(isinstance(self.section.tts_json, list))

# Chapters
    def test_chapter_instance_exists(self):
        self.assertTrue(Chapter.objects.get(chapter_code=TEST_CHAPTER_CODE))

    def test_self_chapter_is_and_instance_of_Chapter(self):
        self.assertTrue(isinstance(self.chapter, Chapter))

    def test_chapter_has_the_correct_title(self):
        self.assertTrue(self.chapter.title, TEST_CHAPTER_DESCRIPTION)

    def test_chapter_has_the_correct_hierachy_key(self):
        self.assertEqual(self.chapter.hierarchy_key, "chapter-{0}".format(self.chapter.pk))

    def test_chapter_has_tts_obj_value(self):
        # self.assertTrue(isinstance(self.chapter.tts_obj, ChapterJson))
        self.assertFalse(isinstance(self.chapter.tts_json, str))

    def test_chapter_has_the_correct_harmonized_code(self):
        self.assertTrue(self.chapter.harmonized_code, TEST_CHAPTER_CODE)

    def test_chapter_has_hierarchy_children(self):
        self.assertTrue(len(self.chapter.get_hierarchy_children()) > 0)

    def test_chapter_has_the_correct_hierarchy_url(self):
        self.assertEqual(self.chapter.get_hierarchy_url(TEST_COUNTRY_CODE),
                         "/search/country/au/hierarchy/chapter-{0}".format(self.chapter.pk))

# HEADINGS
    def test_heading_instance_exists(self):
        self.assertTrue(Heading.objects.get(heading_code=TEST_HEADING_CODE))

    def test_self_heading_is_and_instance_of_Heading(self):
        self.assertTrue(isinstance(self.heading, Heading))

    def test_heading_instance_exists_with_short_code(self):
        self.assertTrue(Heading.objects.get(heading_code=TEST_HEADING_CODE))

    def test_heading_has_the_correct_title(self):
        self.assertTrue(self.heading.tts_title, TEST_HEADING_DESCRIPTION)

    def test_heading_has_the_correct_hierachy_key(self):
        self.assertEqual(self.heading.hierarchy_key, "heading-{0}".format(self.heading.pk))

    def test_heading_has_tts_obj_is_an_instance_of_HeadingJson(self):
        # self.assertTrue(isinstance(self.heading.tts_obj, HeadingJson))
        self.assertEqual(self.heading.tts_json, None)

    def test_heading_has_the_correct_harmonized_code(self):
        self.assertTrue(self.heading.harmonized_code, TEST_HEADING_CODE)

    def test_heading_has_hierarchy_children(self):
        self.assertTrue(len(self.heading.get_hierarchy_children()) > 0)

    def test_heading_has_the_correct_hierarchy_url(self):
        self.assertEqual(self.heading.get_hierarchy_url(TEST_COUNTRY_CODE),
                         "/search/country/au/hierarchy/heading-{0}".format(self.heading.pk))

    # def test_heading_has_correct_absolute_url(self):
    #     kwargs = {'heading_code': TEST_HEADING_CODE}
    #     self.assertEqual(self.heading.get_absolute_url(), "/search/country/au/hierarchy/heading-8")

# SUBHEADINGS
    def test_subheading_instance_exists(self):
        self.assertTrue(SubHeading.objects.get(commodity_code=TEST_SUBHEADING_CODE))

    def test_self_subheading_is_and_instance_of_SubHeading(self):
        self.assertTrue(isinstance(self.subheading, SubHeading))

    def test_subheading_has_the_correct_title(self):
        self.assertTrue(self.subheading.tts_title, TEST_SUBHEADING_DESCRIPTION)

    def test_subheading_has_the_correct_hierachy_key(self):
        self.assertEqual(self.subheading.hierarchy_key, "sub_heading-{0}".format(self.subheading.pk))

    def test_subheading_has_tts_heading_obj_is_an_instance_of_SubHeadingJson(self):
        # self.assertTrue(isinstance(self.subheading.tts_heading_obj, CommodityHeadingJson))
        self.assertFalse(isinstance(self.subheading.tts_heading_json, str))

    def test_subheading_has_the_correct_harmonized_code(self):
        self.assertTrue(self.subheading.harmonized_code, TEST_SUBHEADING_CODE)

    def test_subheading_has_hierarchy_children(self):
        self.assertTrue(len(self.subheading.get_hierarchy_children()) > 0)

    def test_subheading_has_the_correct_hierarchy_url(self):
        self.assertEqual(self.subheading.get_hierarchy_url(TEST_COUNTRY_CODE),
                         "/search/country/au/hierarchy/sub_heading-{}".format(self.subheading.pk))

    def test_subheading_has_parent(self):
        self.assertTrue(isinstance(self.subheading.get_parent(), SubHeading) or
                        isinstance(self.subheading.get_parent(), Heading))


import json
import logging
import os
import re

from django.apps import apps
from django.conf import settings
from django.test import TestCase
from mixer.backend.django import mixer

from commodities.models import Commodity
from hierarchy.models import SubHeading, Heading, Section, Chapter
from trade_tariff_service.tts_api import CommodityJson

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)

def get_data(file_path):
    with open(file_path) as f:
        json_data = json.load(f)
    return json_data


def create_instance(data, app_name, model_name):
    model = apps.get_model(app_label=app_name, model_name=model_name)
    instance = model(**data)
    return instance


class TestHeadingModel(TestCase):

    """
    Test Heading Integration
    """

    def setUp(self):
        """
        To test fully test a commodity we need to load a parent subheading and its parent heading and save the
        relationships between the three model instances
        :return:
        """
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

    def test_self_heading_is_and_instance_of_Heading(self):
        self.assertTrue(isinstance(self.heading, Heading))

    def test_heading_exists(self):
        self.assertEqual(str(self.heading), "Heading {0}".format(settings.TEST_HEADING_CODE))


class TestSubHeadingModel(TestCase):

    """
    Test SubHeading Integration
    """

    def setUp(self):
        """
        To test fully test a commodity we need to load a parent subheading and its parent heading and save the
        relationships between the three model instances
        :return:
        """
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


    def test_subheading_exists(self):
        self.assertEqual(str(self.subheading), "Sub Heading {0}".format(settings.TEST_SUBHEADING_CODE))

    def test_heading_exists(self):
        self.assertEqual(str(self.heading), "Heading {0}".format(settings.TEST_HEADING_CODE))

    def test_subheading_has_heading_parent(self):
        self.assertEqual(self.subheading.heading_id, self.heading.id)

        with open(file_path) as f:
            json_data = json.load(f)
        return json_data

class TestCommodityModel(TestCase):

    """
    Test Commodity Integration
        instance.save()
    """

    def setUp(self):
        """
        To test fully test a commodity we need to load a parent subheading and its parent heading and save the
        relationships between the three model instances
        :return:
        """
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
            chapter=self.chapter,
            description=settings.TEST_HEADING_DESCRIPTION,
            tts_json=json.dumps(get_data(settings.HEADING_STRUCTURE)),
        )

        self.subheading = mixer.blend(
            SubHeading,
            commodity_code="0101210000",
            heading=self.heading,
            tts_json=json.dumps(get_data(settings.SUBHEADING_STRUCTURE)),
        )
        self.commodity = mixer.blend(
            Commodity,
            commodity_code="0101210000",
            tts_json=json.dumps(get_data(settings.COMMODITY_STRUCTURE)),
            tts_heading_json=json.dumps(get_data(settings.HEADING_STRUCTURE)),
            parent_subheading=self.subheading,
            description=settings.TEST_COMMODITY_DESCRIPTION
        )

    def test_self_commodity_is_and_instance_of_Commodity(self):
        self.assertTrue(isinstance(self.commodity, Commodity))

    def test_commodity_instance_exists(self):
        self.assertTrue(Commodity.objects.get(commodity_code=settings.TEST_COMMODITY_CODE))

    def test_commodity_get_absolute_url(self):
        self.assertEqual(self.commodity.get_absolute_url(settings.TEST_COUNTRY_CODE),
                         "/country/au/commodity/{0}".format(settings.TEST_COMMODITY_CODE))

    def test_commodity_in_db_and_self_commodity_are_the_same(self):
        self.assertEquals(Commodity.objects.get(commodity_code=settings.TEST_COMMODITY_CODE), self.commodity)

    def test_string_representation_a_commodity(self):
        self.assertEqual(str(self.commodity), "Commodity {0}".format(settings.TEST_COMMODITY_CODE))

    def test_verbose_name_plural_of_the_Commodity_model(self):
        self.assertEqual(str(Commodity._meta.verbose_name_plural), "commodities")

    def test_commodity_has_the_correct_parent_model_instance(self):
        self.assertTrue(self.commodity.heading or self.commodity.parent_subheading)

    def test_commodity_has_related_parent_subheading_instance(self):
        self.assertTrue(self.commodity.parent_subheading, None)
        self.assertTrue(isinstance(self.commodity.parent_subheading, SubHeading))

    def test_commodity_does_not_have_a_related_heading_instance(self):
        self.assertEqual(self.commodity.heading, None)

    def test_commodity_parent_subheading_description_is_correct(self):
        self.assertTrue(self.commodity.parent_subheading.description, settings.TEST_SUBHEADING_DESCRIPTION)

    def test_heading_exists(self):
        self.assertEqual(str(self.heading), "Heading {0}".format(settings.TEST_HEADING_CODE))

    # def test_commodity_parent_subheading_has_parent_heading(self):

        self.assertEqual(str(self.subheading), "Sub Heading {0}".format(settings.TEST_SUBHEADING_CODE))

    def test_subheading_has_heading_parent(self):
        self.assertEqual(str(self.subheading.heading), "Heading {0}".format(settings.TEST_HEADING_CODE))
        self.assertTrue(self.subheading.heading)

    def test_commodity_parent_subheading_has_parent_heading(self):
    #     self.assertEqual(self.commodity.parent_subheading.heading, self.heading)

    def test_commodity_has_correct_heading(self):

        # logger.info(" COM: {}".format(self.commodity))
        # logger.info("par: {}".format(self.commodity.parent_subheading))
        heading = self.commodity.get_heading()
        self.assertEquals(
            settings.TEST_HEADING_DESCRIPTION,
            heading.description
        )

    def test_commodity_description_is_correct(self):
        self.assertEqual(self.commodity.description, settings.TEST_COMMODITY_DESCRIPTION)

    def test_commodity_tts_heading_description(self):
        self.assertEqual(self.commodity.get_heading().description, settings.TEST_HEADING_DESCRIPTION)

    def test_commodity_tts_obj_is_not_empty(self):
        self.assertNotEqual(self.commodity.tts_obj, None)

    def test_commodity_tts_obj_is_CommodityJson(self):
        self.assertTrue(isinstance(self.commodity.tts_obj, CommodityJson))

    def test_commodity_code_splt_is_correct(self):
        self.assertTrue(self.commodity.commodity_code_split, settings.TEST_COMMODITY_CODE_SPLIT)

    def test_commodity_get_absolute_url(self):
        self.assertEqual(self.commodity.get_absolute_url(settings.TEST_COUNTRY_CODE),
                         "/country/au/commodity/{0}".format(settings.TEST_COMMODITY_CODE))

    def test_commodity_0101210000_hierarchy_key(self):
        self.assertEqual(self.commodity.hierarchy_key, "commodity-{0}".format(self.commodity.pk))

"""
#TODO: move to tts_serivce tests
    def test_commodity_structure_file_exists(self):
        self.assertTrue(os.path.isfile(COMMODITY_STRUCTURE))

    def test_subheading_structure_file_exists(self):
        self.assertTrue(os.path.isfile(SUBHEADING_STRUCTURE))

    def test_heading_structure_file_exists(self):
        self.assertTrue(os.path.isfile(HEADING_STRUCTURE))

    def test_commodity_data_file_exists(self):
        self.assertTrue(os.path.isfile(COMMODITY_DATA))

    def test_commodity_structure_is_a_dict(self):
        self.assertTrue(isinstance(self.get_data(COMMODITY_STRUCTURE), dict))

    def test_commodity_structure_data_has_correct_fields(self):
        self.assertTrue(set([True for field in self.get_data(COMMODITY_STRUCTURE).keys()
                             if Commodity._meta.get_field(field)]))

    def test_subheading_structure_is_a_dict(self):
        self.assertTrue(isinstance(self.get_data(SUBHEADING_STRUCTURE), dict))

    def test_subheading_structure_data_has_correct_fields(self):
        self.assertTrue(set([True for field in self.get_data(SUBHEADING_STRUCTURE).keys()
                             if SubHeading._meta.get_field(field)]))

    def test_heading_structure_is_a_dict(self):
        self.assertTrue(isinstance(self.get_data(HEADING_STRUCTURE), dict))

    def test_heading_structure_data_has_correct_fields(self):
        self.assertTrue(set([True for field in self.get_data(HEADING_STRUCTURE).keys()
                             if Heading._meta.get_field(field)]))

    def test_commodity_data_is_a_dict(self):
        self.assertTrue(isinstance(self.get_data(COMMODITY_DATA), dict))

    def test_create_commodity_instance(self):
        struct_data = self.get_data(COMMODITY_STRUCTURE)
        instance = self.create_instance(struct_data, 'commodities', 'Commodity')
        data = self.get_data(COMMODITY_DATA)
        instance.tts_json = data
        instance.save()
        self.assertTrue(isinstance(instance, Commodity))

    def test_create_subheading_instance(self):
        struct_data = self.get_data(SUBHEADING_STRUCTURE)
        instance = self.create_instance(struct_data, 'hierarchy', 'SubHeading')
        self.assertTrue(isinstance(instance, SubHeading))

    def test_create_heading_instance(self):
        struct_data = self.get_data(HEADING_STRUCTURE)
        instance = self.create_instance(struct_data, 'hierarchy', 'Heading')
        self.assertTrue(isinstance(instance, Heading))

"""

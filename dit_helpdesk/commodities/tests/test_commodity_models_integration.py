import json
import logging

from django.apps import apps
from django.conf import settings
from django.test import TestCase
from mixer.backend.django import Mixer

from commodities.models import Commodity
from hierarchy.models import SubHeading, Heading, Section, Chapter
from hierarchy.helpers import create_nomenclature_tree
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
        self.tree = create_nomenclature_tree("UK")

        self.heading_model_mixer = Mixer()

        for model in [Section, Chapter, Heading, SubHeading, Commodity]:
            self.heading_model_mixer.register(model, nomenclature_tree=self.tree)

        self.section = self.heading_model_mixer.blend(Section, section_id=1)
        self.chapter = self.heading_model_mixer.blend(
            Chapter, chapter_code="0100000000", section=self.section
        )

        self.heading = self.heading_model_mixer.blend(
            Heading, heading_code="0101000000", chapter=self.chapter
        )

    def test_self_heading_is_and_instance_of_Heading(self):
        self.assertTrue(isinstance(self.heading, Heading))

    def test_heading_exists(self):
        self.assertEqual(
            str(self.heading), "Heading {0}".format(settings.TEST_HEADING_CODE)
        )


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
        self.tree = create_nomenclature_tree("UK")

        self.subheading_model_mixer = Mixer()

        for model in [Section, Chapter, Heading, SubHeading, Commodity]:
            self.subheading_model_mixer.register(model, nomenclature_tree=self.tree)

        self.section = self.subheading_model_mixer.blend(Section, section_id=1)
        self.chapter = self.subheading_model_mixer.blend(
            Chapter, chapter_code="0100000000", section=self.section
        )

        self.heading = self.subheading_model_mixer.blend(
            Heading, heading_code="0101000000", chapter=self.chapter
        )

        self.subheading = self.subheading_model_mixer.blend(
            SubHeading, commodity_code="0101210000", heading=self.heading
        )

    def test_subheading_exists(self):
        self.assertEqual(
            str(self.subheading),
            "Sub Heading {0}".format(settings.TEST_SUBHEADING_CODE),
        )

    def test_heading_exists(self):
        self.assertEqual(
            str(self.heading), "Heading {0}".format(settings.TEST_HEADING_CODE)
        )

    def test_subheading_has_heading_parent(self):
        self.assertEqual(self.subheading.heading_id, self.heading.id)


class TestCommodityModel(TestCase):

    """
    Test Commodity Integration
    """

    def setUp(self):
        """
        To test fully test a commodity we need to load a parent subheading and its parent heading and save the
        relationships between the three model instances
        :return:
        """
        self.tree = create_nomenclature_tree("UK")

        self.commodity_model_mixer = Mixer()

        for model in [Section, Chapter, Heading, SubHeading, Commodity]:
            self.commodity_model_mixer.register(model, nomenclature_tree=self.tree)

        self.section = self.commodity_model_mixer.blend(Section, section_id=1)
        self.chapter = self.commodity_model_mixer.blend(
            Chapter, chapter_code="0100000000", section=self.section
        )

        self.heading = self.commodity_model_mixer.blend(
            Heading,
            heading_code="0101000000",
            chapter=self.chapter,
            description=settings.TEST_HEADING_DESCRIPTION,
            tts_json=json.dumps(get_data(settings.HEADING_STRUCTURE)),
        )

        self.subheading = self.commodity_model_mixer.blend(
            SubHeading,
            commodity_code="0101210000",
            heading=self.heading,
            tts_json=json.dumps(get_data(settings.SUBHEADING_STRUCTURE)),
        )
        self.commodity = self.commodity_model_mixer.blend(
            Commodity,
            commodity_code="0101210000",
            tts_json=json.dumps(get_data(settings.COMMODITY_STRUCTURE)),
            parent_subheading=self.subheading,
            description=settings.TEST_COMMODITY_DESCRIPTION,
            goods_nomenclature_sid=12345,
        )

    def test_self_commodity_is_and_instance_of_Commodity(self):
        self.assertTrue(isinstance(self.commodity, Commodity))

    def test_commodity_instance_exists(self):
        self.assertTrue(
            Commodity.objects.get(commodity_code=settings.TEST_COMMODITY_CODE)
        )

    def test_commodity_get_absolute_url(self):
        self.assertEqual(
            self.commodity.get_absolute_url(settings.TEST_COUNTRY_CODE),
            "/country/au/commodity/{0}/{1}".format(
                settings.TEST_COMMODITY_CODE, "12345"
            ),
        )

    def test_commodity_in_db_and_self_commodity_are_the_same(self):
        self.assertEquals(
            Commodity.objects.get(commodity_code=settings.TEST_COMMODITY_CODE),
            self.commodity,
        )

    def test_string_representation_a_commodity(self):
        self.assertEqual(
            str(self.commodity), "Commodity {0}".format(settings.TEST_COMMODITY_CODE)
        )

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
        self.assertTrue(
            self.commodity.parent_subheading.description,
            settings.TEST_SUBHEADING_DESCRIPTION,
        )

    def test_commodity_has_correct_heading(self):
        heading = self.commodity.get_heading()
        self.assertEquals(settings.TEST_HEADING_DESCRIPTION, heading.description)

    def test_commodity_description_is_correct(self):
        self.assertEqual(
            self.commodity.description, settings.TEST_COMMODITY_DESCRIPTION
        )

    def test_commodity_tts_heading_description(self):
        self.assertEqual(
            self.commodity.get_heading().description, settings.TEST_HEADING_DESCRIPTION
        )

    def test_commodity_tts_obj_is_not_empty(self):
        self.assertNotEqual(self.commodity.tts_obj, None)

    def test_commodity_tts_obj_is_CommodityJson(self):
        self.assertTrue(isinstance(self.commodity.tts_obj, CommodityJson))

    def test_commodity_code_splt_is_correct(self):
        self.assertTrue(
            self.commodity.commodity_code_split, settings.TEST_COMMODITY_CODE_SPLIT
        )

    def test_commodity_0101210000_hierarchy_key(self):
        self.assertEqual(
            self.commodity.hierarchy_key, "commodity-{0}".format(self.commodity.pk)
        )

import json
import logging

from django.conf import settings
from django.test import Client, TestCase

from commodities.models import Commodity
from countries.models import Country

from ..helpers import create_nomenclature_tree
from ..models import Section, Chapter, Heading, SubHeading

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)

TEST_COMMODITY_CODE = "0101210000"
TEST_SUBHEADING_CODE = "0101210000"


def get_data(file_path, tree):
    with open(file_path) as f:
        json_data = json.load(f)

    json_data["nomenclature_tree_id"] = tree.pk

    return json_data


def create_instance(data, model_class):
    skip_attributes = ["tts_json"]
    filtered_data = {
        k: v
        for k, v in data.items()
        if k not in skip_attributes
    }
    instance = model_class(**filtered_data)
    instance.save()
    return instance


class HierarchyViewTestCase(TestCase):
    """
    Test Hierarchy view
    """

    def setUp(self):
        """
        To test fully test a commodity we need to load a parent subheading and its parent heading and save the
        relationships between the three model instances
        :return:
        """
        self.tree = create_nomenclature_tree(region='UK')

        self.section = create_instance(
            get_data(settings.SECTION_STRUCTURE, self.tree), Section
        )

        self.chapter = create_instance(
            get_data(settings.CHAPTER_STRUCTURE, self.tree), Chapter
        )
        self.chapter.section_id = self.section.pk
        self.chapter.save()

        self.heading = create_instance(
            get_data(settings.HEADING_STRUCTURE, self.tree), Heading
        )
        self.heading.chapter_id = self.chapter.pk
        self.heading.save()

        self.subheading = create_instance(
            get_data(settings.SUBHEADING_STRUCTURE, self.tree), SubHeading
        )
        self.subheading.heading_id = self.heading.id
        self.subheading.save()

        self.commodity = create_instance(
            get_data(settings.COMMODITY_STRUCTURE, self.tree), Commodity
        )
        self.commodity.parent_subheading_id = self.subheading.id
        self.commodity.tts_json = json.dumps(get_data(settings.COMMODITY_DATA, self.tree))

        self.commodity.save()

        self.client = Client()

    def test_section_data_exists(self):
        self.assertTrue(Section.objects.count() > 0)

    def test_chapter_data_exists(self):
        self.assertTrue(Chapter.objects.count() > 0)

    def test_heading_data_exists(self):
        self.assertTrue(Heading.objects.count() > 0)

    def test_subheading_data_exists(self):
        self.assertTrue(SubHeading.objects.count() > 0)

    def test_commodity_data_exists(self):
        self.assertTrue(Commodity.objects.count() > 0)

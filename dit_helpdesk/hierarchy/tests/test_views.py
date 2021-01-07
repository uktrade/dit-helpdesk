import json
import logging

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

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

        self.country = Country.objects.get(country_code="FR")

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


class ChapterDetailViewTestCase(HierarchyViewTestCase):

    def setUp(self):
        super().setUp()

        self.url = reverse(
            "chapter-detail",
            kwargs={
                "country_code": self.country.country_code.lower(),
                "chapter_code": self.chapter.chapter_code,
                "nomenclature_sid": self.chapter.goods_nomenclature_sid,
            }
        )

    def test_commodity_object(self):
        response = self.client.get(self.url)
        ctx = response.context

        self.assertEqual(
            ctx["commodity"],
            self.chapter,
        )
        self.assertEqual(
            ctx["object"],
            self.chapter,
        )

    def test_commodity_object_path(self):
        response = self.client.get(self.url)
        ctx = response.context

        accordion_title = ctx["accordion_title"]
        self.assertEqual(
            accordion_title,
            "Section I: Live animals; animal products",
        )

        hierarchy_context = ctx["hierarchy_context"]
        self.assertInHTML(
            "Live animals",
            hierarchy_context,
        )
        self.assertInHTML(
            "Live horses, asses, mules and hinnies",
            hierarchy_context,
        )

    def test_notes_context_data(self):
        response = self.client.get(self.url)
        ctx = response.context

        self.assertEqual(
            ctx["section_notes"],
            self.section.section_notes,
        )
        self.assertEqual(
            ctx["chapter_notes"],
            self.chapter.chapter_notes,
        )
        self.assertNotIn("heading_notes", ctx)
        self.assertNotIn("commodity_notes", ctx)

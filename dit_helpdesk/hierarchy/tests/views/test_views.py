import json
import logging
import requests
import requests_mock

from contextlib import contextmanager
from unittest import mock

from django.conf import settings
from django.test import Client, TestCase

from commodities.models import Commodity
from core.helpers import patch_tts_json, patch_section_notes
from countries.models import Country

from ...helpers import create_nomenclature_tree
from ...models import Section, Chapter, Heading, SubHeading

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
    filtered_data = {k: v for k, v in data.items() if k not in skip_attributes}
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
        self.tree = create_nomenclature_tree(region=settings.PRIMARY_REGION)

        self.country = Country.objects.get(country_code="FR")

        self.section = create_instance(
            get_data(settings.SECTION_STRUCTURE, self.tree), Section
        )

        self.chapter = create_instance(
            get_data(settings.CHAPTER_STRUCTURE, self.tree), Chapter
        )
        self.chapter.section_id = self.section.pk
        self.chapter.save()
        self.chapter_url = self.chapter.get_detail_url(self.country.country_code)

        self.heading = create_instance(
            get_data(settings.HEADING_STRUCTURE, self.tree), Heading
        )
        self.heading.chapter_id = self.chapter.pk
        self.heading.save()
        self.heading_url = self.heading.get_detail_url(self.country.country_code)

        self.subheading = create_instance(
            get_data(settings.SUBHEADING_STRUCTURE, self.tree), SubHeading
        )
        self.subheading.heading_id = self.heading.id
        self.subheading.save()
        self.subheading_url = self.subheading.get_detail_url(self.country.country_code)

        self.commodity = create_instance(
            get_data(settings.COMMODITY_STRUCTURE, self.tree), Commodity
        )
        self.commodity.parent_subheading_id = self.subheading.id
        self.commodity.tts_json = json.dumps(
            get_data(settings.COMMODITY_DATA, self.tree)
        )
        self.commodity.save()

        self.client = Client()

        with open(settings.TTS_DATA) as f:
            self.tts_response = f.read()

        self.section_note_response = {
            "id": 1,
            "section_id": 1,
            "content": "1. Any reference in this section to a particular genus or species of an \
                animal, except where the context otherwise requires, includes a reference to the young \
                of that genus or species.\r\n2. Except where the context otherwise requires, throughout \
                the nomenclature any reference to 'dried' products also covers products which have \
                been dehydrated, evaporated or freeze-dried.\r\n",
        }

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
    @requests_mock.Mocker()
    def test_commodity_object(self, mock):
        mock.get(
            settings.REQUEST_MOCK_CHAPTER_TTS_URL,
            text=self.tts_response,
        )
        mock.get(
            settings.REQUEST_MOCK_SECTION_URL,
            json=self.section_note_response,
        )
        requests.get(settings.REQUEST_MOCK_CHAPTER_TTS_URL).text
        requests.get(settings.REQUEST_MOCK_SECTION_URL).json

        response = self.client.get(self.chapter_url)
        ctx = response.context

        self.assertEqual(ctx["commodity"], self.chapter)
        self.assertEqual(ctx["object"], self.chapter)

    @requests_mock.Mocker()
    def test_commodity_object_path(self, mock):
        mock.get(
            settings.REQUEST_MOCK_CHAPTER_TTS_URL,
            text=self.tts_response,
        )
        mock.get(
            settings.REQUEST_MOCK_SECTION_URL,
            json=self.section_note_response,
        )
        requests.get(settings.REQUEST_MOCK_CHAPTER_TTS_URL).text
        requests.get(settings.REQUEST_MOCK_SECTION_URL).json

        response = self.client.get(self.chapter_url)
        ctx = response.context

        accordion_title = ctx["accordion_title"]
        self.assertEqual(accordion_title, "Section I: Live animals; animal products")

        hierarchy_context = ctx["hierarchy_context"]
        self.assertInHTML("Live animals", hierarchy_context)
        self.assertNotIn(self.chapter_url, hierarchy_context)
        self.assertInHTML("Live horses, asses, mules and hinnies", hierarchy_context)
        self.assertIn(self.heading_url, hierarchy_context)

    @requests_mock.Mocker()
    def test_notes_context_data(self, mock):
        mock.get(
            settings.REQUEST_MOCK_CHAPTER_TTS_URL,
            text=self.tts_response,
        )
        mock.get(
            settings.REQUEST_MOCK_SECTION_URL,
            json=self.section_note_response,
        )
        requests.get(settings.REQUEST_MOCK_CHAPTER_TTS_URL).text
        requests.get(settings.REQUEST_MOCK_SECTION_URL).json

        response = self.client.get(self.chapter_url)
        ctx = response.context

        self.assertEqual(ctx["section_notes"], self.section.section_notes)
        self.assertEqual(ctx["chapter_notes"], self.chapter.chapter_notes)
        self.assertNotIn("heading_notes", ctx)
        self.assertNotIn("commodity_notes", ctx)


class HeadingDetailViewTestCase(HierarchyViewTestCase):
    @requests_mock.Mocker()
    def test_commodity_object(self, mock):
        mock.get(
            settings.REQUEST_MOCK_HEADING_TTS_URL,
            text=self.tts_response,
        )
        mock.get(
            settings.REQUEST_MOCK_SECTION_URL,
            json=self.section_note_response,
        )
        requests.get(settings.REQUEST_MOCK_HEADING_TTS_URL).text
        requests.get(settings.REQUEST_MOCK_SECTION_URL).json

        response = self.client.get(self.heading_url)
        ctx = response.context

        self.assertEqual(ctx["commodity"], self.heading)
        self.assertEqual(ctx["object"], self.heading)

    @requests_mock.Mocker()
    def test_commodity_object_path(self, mock):
        mock.get(
            settings.REQUEST_MOCK_HEADING_TTS_URL,
            text=self.tts_response,
        )
        mock.get(
            settings.REQUEST_MOCK_SECTION_URL,
            json=self.section_note_response,
        )
        requests.get(settings.REQUEST_MOCK_HEADING_TTS_URL).text
        requests.get(settings.REQUEST_MOCK_SECTION_URL).json

        response = self.client.get(self.heading_url)
        ctx = response.context

        accordion_title = ctx["accordion_title"]
        self.assertEqual(accordion_title, "Section I: Live animals; animal products")

        hierarchy_context = ctx["hierarchy_context"]
        self.assertIn(self.chapter_url, hierarchy_context)
        self.assertInHTML("Live animals", hierarchy_context)
        self.assertInHTML("Live horses, asses, mules and hinnies", hierarchy_context)
        self.assertNotIn(self.heading_url, hierarchy_context)
        self.assertInHTML("Horses", hierarchy_context)
        self.assertIn(self.subheading_url, hierarchy_context)

    @requests_mock.Mocker()
    def test_notes_context_data(self, mock):
        mock.get(
            settings.REQUEST_MOCK_HEADING_TTS_URL,
            text=self.tts_response,
        )
        mock.get(
            settings.REQUEST_MOCK_SECTION_URL,
            json=self.section_note_response,
        )
        requests.get(settings.REQUEST_MOCK_HEADING_TTS_URL).text
        requests.get(settings.REQUEST_MOCK_SECTION_URL).json

        response = self.client.get(self.heading_url)
        ctx = response.context

        self.assertEqual(ctx["section_notes"], self.section.section_notes)
        self.assertEqual(ctx["chapter_notes"], self.chapter.chapter_notes)
        self.assertEqual(ctx["heading_notes"], self.heading.heading_notes)
        self.assertNotIn("commodity_notes", ctx)


class HierarchyNorthernIrelandViewTestCase(HierarchyViewTestCase):
    def setUp(self):
        super().setUp()

        self.tree_eu = create_nomenclature_tree(region=settings.SECONDARY_REGION)

        self.section_eu = create_instance(
            get_data(settings.SECTION_STRUCTURE, self.tree_eu), Section
        )

        self.chapter_eu = create_instance(
            get_data(settings.CHAPTER_STRUCTURE, self.tree_eu), Chapter
        )
        self.chapter_eu.section_id = self.section_eu.pk
        self.chapter_eu.save()

        self.heading_eu_data = get_data(settings.HEADING_STRUCTURE, self.tree_eu)
        self.heading_eu = create_instance(self.heading_eu_data, Heading)
        self.heading_eu.chapter_id = self.chapter_eu.pk
        self.heading_eu.save()
        self.heading_northern_ireland_url = (
            self.heading_eu.get_northern_ireland_detail_url(self.country.country_code)
        )

        self.subheading_eu = create_instance(
            get_data(settings.SUBHEADING_STRUCTURE, self.tree_eu), SubHeading
        )
        self.subheading_eu.heading_id = self.heading_eu.id
        self.subheading_eu.save()
        self.subheading_northern_ireland_url = (
            self.subheading_eu.get_northern_ireland_detail_url(
                self.country.country_code
            )
        )

        self.commodity_eu = create_instance(
            get_data(settings.COMMODITY_STRUCTURE, self.tree_eu), Commodity
        )
        self.commodity_eu.parent_subheading_id = self.subheading_eu.id
        self.commodity_eu.tts_json = json.dumps(
            get_data(settings.COMMODITY_DATA, self.tree_eu)
        )
        self.commodity_eu.save()


class HeadingDetailNorthernIrelandViewTestCase(HierarchyNorthernIrelandViewTestCase):
    def test_eu_commodity_object_update_tts_content(self):
        @contextmanager
        def tts_content_mock(should_update):
            with mock.patch.object(
                Heading, "should_update_tts_content", return_value=should_update
            ), mock.patch.object(Heading, "update_tts_content"), patch_tts_json(
                Heading, settings.HEADINGJSON_DATA
            ), mock.patch.object(
                Section, "section_notes"
            ), patch_section_notes(
                Section
            ):
                yield

        with tts_content_mock(False):
            self.client.get(self.heading_northern_ireland_url)
            self.heading_eu.update_tts_content.assert_not_called()

        with tts_content_mock(True):
            self.client.get(self.heading_northern_ireland_url)
            self.heading_eu.update_tts_content.assert_called()


class SubHeadingDetailViewTestCase(HierarchyViewTestCase):
    @requests_mock.Mocker()
    def test_commodity_object(self, mock):
        mock.get(
            settings.REQUEST_MOCK_HEADING_TTS_URL,
            text=self.tts_response,
        )
        mock.get(
            settings.REQUEST_MOCK_SECTION_URL,
            json=self.section_note_response,
        )
        requests.get(settings.REQUEST_MOCK_HEADING_TTS_URL).text
        requests.get(settings.REQUEST_MOCK_SECTION_URL).json

        response = self.client.get(self.subheading_url)
        ctx = response.context

        self.assertEqual(ctx["commodity"], self.subheading)
        self.assertEqual(ctx["object"], self.subheading)

    @requests_mock.Mocker()
    def test_commodity_object_path(self, mock):
        mock.get(
            settings.REQUEST_MOCK_HEADING_TTS_URL,
            text=self.tts_response,
        )
        mock.get(
            settings.REQUEST_MOCK_SECTION_URL,
            json=self.section_note_response,
        )
        requests.get(settings.REQUEST_MOCK_HEADING_TTS_URL).text
        requests.get(settings.REQUEST_MOCK_SECTION_URL).json

        response = self.client.get(self.subheading_url)
        ctx = response.context

        accordion_title = ctx["accordion_title"]
        self.assertEqual(accordion_title, "Section I: Live animals; animal products")

        hierarchy_context = ctx["hierarchy_context"]
        self.assertIn(self.chapter_url, hierarchy_context)
        self.assertInHTML("Live animals", hierarchy_context)
        self.assertInHTML("Live horses, asses, mules and hinnies", hierarchy_context)
        self.assertIn(self.heading_url, hierarchy_context)
        self.assertInHTML("Horses", hierarchy_context)
        self.assertNotIn(self.subheading_url, hierarchy_context)
        self.assertInHTML("Pure-bred breeding animals", hierarchy_context)

    @requests_mock.Mocker()
    def test_notes_context_data(self, mock):
        mock.get(
            settings.REQUEST_MOCK_HEADING_TTS_URL,
            text=self.tts_response,
        )
        mock.get(
            settings.REQUEST_MOCK_SECTION_URL,
            json=self.section_note_response,
        )
        requests.get(settings.REQUEST_MOCK_HEADING_TTS_URL).text
        requests.get(settings.REQUEST_MOCK_SECTION_URL).json

        response = self.client.get(self.subheading_url)
        ctx = response.context

        self.assertEqual(ctx["section_notes"], self.section.section_notes)
        self.assertEqual(ctx["chapter_notes"], self.chapter.chapter_notes)
        self.assertEqual(ctx["heading_notes"], self.subheading.heading_notes)
        self.assertNotIn("commodity_notes", ctx)


class SubHeadingDetailNorthernIrelandViewTestCase(HierarchyNorthernIrelandViewTestCase):
    def test_eu_commodity_object_update_tts_content(self):
        @contextmanager
        def tts_content_mock(should_update):
            with mock.patch.object(
                SubHeading, "should_update_tts_content", return_value=should_update
            ), mock.patch.object(SubHeading, "update_tts_content"), patch_tts_json(
                SubHeading, settings.SUBHEADINGJSON_DATA
            ), mock.patch.object(
                Section, "section_notes"
            ), patch_section_notes(
                Section
            ):
                yield

        with tts_content_mock(False):
            self.client.get(self.subheading_northern_ireland_url)
            self.subheading_eu.update_tts_content.assert_not_called()

        with tts_content_mock(True):
            self.client.get(self.subheading_northern_ireland_url)
            self.subheading_eu.update_tts_content.assert_called()

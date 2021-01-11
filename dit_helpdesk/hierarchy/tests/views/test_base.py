from unittest import mock

from mixer.backend.django import mixer

from django.test import modify_settings, override_settings, TestCase
from django.urls import reverse

from countries.models import Country

from ...helpers import create_nomenclature_tree, TABLE_COLUMN_TITLES
from ...models import Chapter, Heading, Section
from ...views.base import BaseCommodityObjectDetailView, BaseSectionedCommodityObjectDetailView
from ...views.sections import CommodityDetailSection


MOCK_NOTES = {
    "section_notes": "SECTION NOTES",
    "chapter_notes": "CHAPTER NOTES",
    "heading_notes": "HEADING NOTES",
}


class TestBaseCommodityObjectDetailView(BaseCommodityObjectDetailView):
    model = Chapter
    template_name = "hierarchy/test_base_commodity_object_detail.html"

    def get_notes_context_data(self, commodity_object):
        return MOCK_NOTES


@modify_settings(
    INSTALLED_APPS={
        "append": ["hierarchy.tests.views"],
    }
)
@override_settings(ROOT_URLCONF="hierarchy.tests.views.urls")
class BaseCommodityObjectDetailViewTestCase(TestCase):

    def setUp(self):
        super().setUp()

        self.country = Country.objects.all().first()

        tree = create_nomenclature_tree()

        self.section = mixer.blend(
            Section,
            nomenclature_tree=tree,
        )
        self.chapter = mixer.blend(
            Chapter,
            nomenclature_tree=tree,
            chapter_code="0100000000",
            goods_nomenclature_sid="1",
        )
        self.heading = mixer.blend(
            Heading,
            nomenclature_tree=tree,
            heading_code="0101000000",
            goods_nomenclature_sid="2",
        )

        mock_get_commodity_object_path = mock.patch.object(
            TestBaseCommodityObjectDetailView,
            "get_commodity_object_path",
            return_value=[
                [self.heading],
                [self.chapter],
                [self.section],
            ],
        )
        mock_get_commodity_object_path.start()
        self.mock_get_commodity_object_path = mock_get_commodity_object_path

    def tearDown(self):
        self.mock_get_commodity_object_path.stop()

    def get_url(self, country_code=None, commodity_code=None, nomenclature_sid=None):
        if not country_code:
            country_code = self.country.country_code

        if not commodity_code:
            commodity_code = self.chapter.commodity_code

        if not nomenclature_sid:
            nomenclature_sid = self.chapter.goods_nomenclature_sid

        return reverse(
            "test-base-commodity-object-detail-view",
            kwargs={
                "country_code": country_code,
                "commodity_code": commodity_code,
                "nomenclature_sid": nomenclature_sid,
            },
        )

    def test_country_does_not_exist(self):
        country_code = "XT"

        with self.assertRaises(Country.DoesNotExist):
            Country.objects.get(country_code=country_code)

        url = self.get_url(country_code=country_code)
        with mock.patch("hierarchy.views.base.messages.error") as mock_messages_error:
            response = self.client.get(url)

        mock_messages_error.assert_called_once_with(
            response.wsgi_request,
            "Invalid originCountry",
        )

        self.assertRedirects(
            response,
            reverse("choose-country"),
        )

    def test_commodity_object_does_not_exist(self):
        commodity_code = "1234567890"
        nomenclature_sid = "12345"

        with self.assertRaises(Chapter.DoesNotExist):
            Chapter.objects.get(
                chapter_code=commodity_code,
                goods_nomenclature_sid=nomenclature_sid,
            )

        url = self.get_url(
            commodity_code=commodity_code,
            nomenclature_sid=nomenclature_sid,
        )
        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_update_tts_content(self):
        url = self.get_url()

        with mock.patch.object(Chapter, "should_update_tts_content") as mock_should_update_tts_content, \
            mock.patch.object(Chapter, "update_tts_content") as mock_update_tts_content:
            mock_should_update_tts_content.return_value = False
            self.client.get(url)
            mock_update_tts_content.assert_not_called()

        with mock.patch.object(Chapter, "should_update_tts_content") as mock_should_update_tts_content, \
            mock.patch.object(Chapter, "update_tts_content") as mock_update_tts_content:
            mock_should_update_tts_content.return_value = True
            self.client.get(url)
            mock_update_tts_content.assert_called()

    def test_context_data(self):
        eu_commodity_link = "http://example.com/mock-eu-commodity-link"

        with mock.patch.object(Chapter, "should_update_tts_content"), \
            mock.patch.object(Chapter, "update_tts_content"), \
            mock.patch("hierarchy.views.base.get_eu_commodity_link") as mock_get_eu_commodity_link:
            mock_get_eu_commodity_link.return_value = eu_commodity_link

            response = self.client.get(self.get_url())

        ctx = response.context

        self.assertEqual(
            ctx["selected_origin_country"],
            self.country.country_code,
        )
        self.assertEqual(
            ctx["selected_origin_country_name"],
            self.country.name,
        )

        self.assertEqual(
            ctx["accordion_title"],
            f"Section {self.section.roman_numeral}: {self.section.title.capitalize()}"
        )

        self.assertEqual(
            ctx["commodity"],
            self.chapter,
        )

        self.assertEqual(
            ctx["is_eu_member"],
            self.country.is_eu,
        )
        mock_get_eu_commodity_link.assert_called_once_with(self.chapter, self.country)
        self.assertEqual(
            ctx["eu_regulations_link"],
            eu_commodity_link,
        )

        self.assertEqual(
            ctx["section_notes"],
            MOCK_NOTES["section_notes"],
        )
        self.assertEqual(
            ctx["chapter_notes"],
            MOCK_NOTES["chapter_notes"],
        )
        self.assertEqual(
            ctx["heading_notes"],
            MOCK_NOTES["heading_notes"],
        )

        self.assertEqual(
            ctx["column_titles"],
            TABLE_COLUMN_TITLES,
        )

    def test_context_object_name(self):
        with mock.patch.object(Chapter, "should_update_tts_content"), \
            mock.patch.object(Chapter, "update_tts_content"):
            response = self.client.get(self.get_url())
            self.assertNotIn("context_object", response.context)

        with mock.patch.object(Chapter, "should_update_tts_content"), \
            mock.patch.object(Chapter, "update_tts_content"), \
            mock.patch.object(
                TestBaseCommodityObjectDetailView,
                "context_object_name",
                new_callable=mock.PropertyMock,
            ) as mock_context_object_name:
            mock_context_object_name.return_value = "context_object"
            response = self.client.get(self.get_url())
            self.assertEqual(
                response.context["context_object"],
                self.chapter,
            )


class DisplayedSection(CommodityDetailSection):
    def get_menu_items(self):
        return [
            ("Menu item", "not_shown_menu_item"),
            ("Another menu item", "another_not_shown_menu_item"),
        ]

    def get_modals_context_data(self):
        return [
            {
                "section_modals_show_me": "section_modals_me_show",
            },
            {
                "section_another_modals_not_show_me": "section_another_modals_me_show",
            }
        ]

    def get_context_data(self):
        return {
            "section_show_me": "section_me_show",
            "another_section_show_me": "another_section_me_show",
        }


class ShouldNotBeDisplayedSection(CommodityDetailSection):
    should_be_displayed = False

    def get_menu_items(self):
        return [
            ("Not shown menu item", "not_shown_menu_item"),
            ("Another not shown menu item", "another_not_shown_menu_item"),
        ]

    def get_modals_context_data(self):
        return [
            {
                "section_modals_not_show_me": "section_modals_me_show_not",
            },
            {
                "section_another_modals_not_show_me": "section_another_modals_me_show_not",
            }
        ]

    def get_context_data(self):
        return {
            "section_do_not_show_me": "section_me_show_not",
            "another_section_do_not_show_me": "another_section_me_show_not",
        }


class TestBaseSectionedCommodityObjectDetailView(BaseSectionedCommodityObjectDetailView):
    model = Chapter
    sections = [
        DisplayedSection,
        ShouldNotBeDisplayedSection,
    ]
    template_name = "hierarchy/test_base_sectioned_commodity_object_detail.html"


@modify_settings(
    INSTALLED_APPS={
        "append": ["hierarchy.tests.views"],
    }
)
@override_settings(ROOT_URLCONF="hierarchy.tests.views.urls")
class BaseSectionedCommodityObjectDetailViewTestCase(TestCase):

    def setUp(self):
        super().setUp()

        self.country = Country.objects.all().first()

        tree = create_nomenclature_tree()

        self.section = mixer.blend(
            Section,
            nomenclature_tree=tree,
        )
        self.chapter = mixer.blend(
            Chapter,
            nomenclature_tree=tree,
            chapter_code="0100000000",
            goods_nomenclature_sid="1",
        )
        self.heading = mixer.blend(
            Heading,
            nomenclature_tree=tree,
            heading_code="0101000000",
            goods_nomenclature_sid="2",
        )

        mock_get_commodity_object_path = mock.patch.object(
            TestBaseSectionedCommodityObjectDetailView,
            "get_commodity_object_path",
            return_value=[
                [self.heading],
                [self.chapter],
                [self.section],
            ],
        )
        mock_get_commodity_object_path.start()
        self.mock_get_commodity_object_path = mock_get_commodity_object_path

    def tearDown(self):
        self.mock_get_commodity_object_path.stop()

    def get_url(self, country_code=None, commodity_code=None, nomenclature_sid=None):
        if not country_code:
            country_code = self.country.country_code

        if not commodity_code:
            commodity_code = self.chapter.commodity_code

        if not nomenclature_sid:
            nomenclature_sid = self.chapter.goods_nomenclature_sid

        return reverse(
            "test-base-sectioned-commodity-object-detail-view",
            kwargs={
                "country_code": country_code,
                "commodity_code": commodity_code,
                "nomenclature_sid": nomenclature_sid,
            },
        )

    def test_sections_init(self):
        MockSection = mock.MagicMock()
        AnotherMockSection = mock.MagicMock()

        with mock.patch.object(
            TestBaseSectionedCommodityObjectDetailView,
            "sections",
            new_callable=mock.PropertyMock(return_value=[MockSection, AnotherMockSection]),
        ):
            self.client.get(self.get_url())

        MockSection.assert_called_once_with(self.country, self.chapter)
        AnotherMockSection.assert_called_once_with(self.country, self.chapter)

    def test_context_data(self):
        response = self.client.get(self.get_url())
        ctx = response.context

        self.assertEqual(
            ctx["section_show_me"],
            "section_me_show",
        )
        self.assertEqual(
            ctx["another_section_show_me"],
            "another_section_me_show",
        )

        self.assertNotIn(
            "section_do_not_show_me",
            ctx,
        )
        self.assertNotIn(
            "another_section_do_not_show_me",
            ctx,
        )

    def test_sections_context_data(self):
        response = self.client.get(self.get_url())
        sections = response.context["sections"]

        self.assertEqual(len(sections), 1)

        section = sections[0]
        self.assertIsInstance(section, DisplayedSection)

    def test_sections_menu_items_context_data(self):
        response = self.client.get(self.get_url())
        section_menu_items = response.context["section_menu_items"]

        self.assertEqual(
            section_menu_items,
            [
                ('Menu item', 'not_shown_menu_item'),
                ('Another menu item', 'another_not_shown_menu_item'),
            ],
        )

    def test_modals_context_data(self):
        response = self.client.get(self.get_url())
        modals = response.context["modals"]

        self.assertEqual(
            modals["section_modals_show_me"],
            "section_modals_me_show",
        )
        self.assertEqual(
            modals["section_another_modals_not_show_me"],
            "section_another_modals_me_show",
        )

        self.assertNotIn(
            "section_modals_not_show_me",
            modals,
        )
        self.assertNotIn(
            "section_modals_not_show_me",
            modals,
        )

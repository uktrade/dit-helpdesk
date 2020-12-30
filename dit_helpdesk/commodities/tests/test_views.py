import json
import logging

from datetime import datetime, timezone
from unittest.mock import PropertyMock, patch

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from mixer.backend.django import mixer

from commodities.models import Commodity
from countries.models import Country
from hierarchy.models import Section, Chapter, Heading, SubHeading
from hierarchy.views import _commodity_code_html
from hierarchy.helpers import create_nomenclature_tree
from rules_of_origin.models import OldRule, OldRulesGroup, OldRulesGroupMember, OldRulesDocument

logger = logging.getLogger(__name__)


def get_data(file_path):
    """This retrieves JSON data for only a single nomenclature object"""
    with open(file_path) as f:
        json_data = json.load(f)

    return json_data


class CommodityViewTestCase(TestCase):

    """
    Test Commodity View
    """

    def create_instance(self, model_class, data):
        instance = model_class.objects.create(nomenclature_tree=self.tree, **data)
        return instance

    def setUp(self):
        """
        To test fully test a commodity we need to load a parent subheading and its parent heading and save the
        relationships between the three model instances
        :return:
        """
        self.tree = create_nomenclature_tree(region='UK')

        self.section = self.create_instance(
            Section,
            get_data(settings.SECTION_STRUCTURE),
        )

        self.chapter = self.create_instance(
            Chapter,
            get_data(settings.CHAPTER_STRUCTURE),
        )
        self.chapter.section_id = self.section.pk
        self.chapter.save()

        self.heading = self.create_instance(
            Heading,
            get_data(settings.HEADING_STRUCTURE),
        )
        self.heading.chapter_id = self.chapter.id
        self.heading.save()

        self.subheading = self.create_instance(
            SubHeading,
            get_data(settings.SUBHEADING_STRUCTURE),
        )
        self.subheading.heading_id = self.heading.id
        self.subheading.save()

        self.commodity = self.create_instance(
            Commodity,
            get_data(settings.COMMODITY_STRUCTURE),
        )
        self.commodity.parent_subheading_id = self.subheading.id
        self.commodity.goods_nomenclature_sid = 12345
        self.commodity.save()

        self.mock_commodity_tts_json = patch.object(
            Commodity,
            "tts_json",
            new_callable=PropertyMock(return_value=json.dumps(get_data(settings.COMMODITY_DATA))),
        )
        self.mock_commodity_tts_json.start()

        self.client = Client()
        self.url = reverse(
            "commodity-detail",
            kwargs={
                "commodity_code": settings.TEST_COMMODITY_CODE,
                "country_code": settings.TEST_COUNTRY_CODE,
                "nomenclature_sid": 12345,
            },
        )

    def tearDown(self):
        super().tearDown()

        self.mock_commodity_tts_json.stop()

    fixtures = [settings.COUNTRIES_DATA]

    def test_fixtures_load_countries_data(self):
        self.assertTrue(Country.objects.count() > 0)

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

    def test_commodity_detail_view(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_commodity_detail_template_has_the_correct_data(self):
        resp = self.client.get(self.url)
        self.assertInHTML(
            resp.context["commodity"].description, resp.content.decode("utf-8")
        )

    def test_commodity_detail_receives_the_correct_country_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(
            resp.context["selected_origin_country"], settings.TEST_COUNTRY_CODE
        )

    def test_commodity_detail_has_the_correct_commodity_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(
            resp.context["commodity"].commodity_code, settings.TEST_COMMODITY_CODE
        )

    def test_commodity_detail_has_the_selected_country_origin_name(self):
        resp = self.client.get(self.url)
        self.assertEqual(
            resp.context["selected_origin_country_name"], settings.TEST_COUNTRY_NAME
        )

    def test_commodity_detail_without_country_code(self):
        self.assertRaises(
            NoReverseMatch,
            lambda: self.client.get(
                reverse("commodity-detail"),
                kwargs={"commodity_code": settings.TEST_COMMODITY_CODE},
            ),
        )

    def test_commodity_detail_without_commodity_code(self):
        self.assertRaises(
            NoReverseMatch,
            lambda: self.client.get(
                reverse("commodity-detail"),
                kwargs={
                    "country_code": settings.TEST_COUNTRY_CODE,
                    "nomenclature_sid": 12345,
                },
            ),
        )

    def test_commodity_detail_with_nonexisting_country_code(self):
        resp = self.client.get(
            reverse(
                "commodity-detail",
                kwargs={
                    "commodity_code": settings.TEST_COMMODITY_CODE,
                    "country_code": "XY",
                    "nomenclature_sid": 12345,
                },
            )
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("choose-country"))

    def test_commodity_detail_update(self):
        commodity = Commodity.objects.get(commodity_code=settings.TEST_COMMODITY_CODE)
        commodity.save()

        with patch.object(Commodity, "should_update_tts_content") as mock_should_update_tts_content, \
            patch.object(Commodity, "update_tts_content") as mock_update_tts_content:
            mock_should_update_tts_content.return_value = True

            resp = self.client.get(
                reverse(
                    "commodity-detail",
                    kwargs={
                        "commodity_code": settings.TEST_COMMODITY_CODE,
                        "country_code": settings.TEST_COUNTRY_CODE,
                        "nomenclature_sid": 12345,
                    },
                )
            )

        self.assertEqual(resp.status_code, 200)
        mock_should_update_tts_content.assert_called_once()
        mock_update_tts_content.assert_called_once()

    def test_commodity_detail_with_rules_or_origin(self):
        country = Country.objects.get(country_code="AF")
        country.has_uk_trade_agreement = True
        country.save()

        rules_group = mixer.blend(OldRulesGroup, description="test rules group")
        rules_group_member = mixer.blend(
            OldRulesGroupMember,
            old_rules_group=rules_group,
            country=country,
        )
        rules_document = mixer.blend(
            OldRulesDocument, description="test rules document", old_rules_group=rules_group
        )

        rule = mixer.blend(OldRule, old_rules_document=rules_document, chapter=self.chapter)
        resp = self.client.get(
            reverse(
                "commodity-detail",
                kwargs={
                    "commodity_code": self.commodity.commodity_code,
                    "country_code": country.country_code,
                    "nomenclature_sid": self.commodity.goods_nomenclature_sid,
                },
            )
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue("old_rules_of_origin" in resp.context)
        self.assertTrue(resp.context["old_rules_of_origin"])

    def test_commodity_code_html_for_commodity(self):
        html = _commodity_code_html(self.commodity.commodity_code)
        code_html = """<span class="app-commodity-code app-hierarchy-tree__commodity-code" aria-label="Commodity code"><span class="app-commodity-code__highlight app-commodity-code__highlight--1">01</span><span class="app-commodity-code__highlight app-commodity-code__highlight--2">01</span><span class="app-commodity-code__highlight app-commodity-code__highlight--3">21</span><span class="app-commodity-code__highlight app-commodity-code__highlight--4"><span class="app-commodity-code__is-blank">00</span></span><span class="app-commodity-code__highlight app-commodity-code__highlight--5"><span class="app-commodity-code__is-blank">00</span></span></span>"""
        self.assertInHTML(code_html, html)

    def test_commodity_code_html_for_heading(self):
        html = _commodity_code_html(self.heading.heading_code)
        code_html = """<span class="app-commodity-code app-hierarchy-tree__commodity-code" aria-label="Commodity code"><span class="app-commodity-code__highlight app-commodity-code__highlight--1">01</span><span class="app-commodity-code__highlight app-commodity-code__highlight--2">01</span><span class="app-commodity-code__highlight app-commodity-code__highlight--3"><span class="app-commodity-code__is-blank">00</span></span><span class="app-commodity-code__highlight app-commodity-code__highlight--4"><span class="app-commodity-code__is-blank">00</span></span><span class="app-commodity-code__highlight app-commodity-code__highlight--5"><span class="app-commodity-code__is-blank">00</span></span></span>"""
        self.assertInHTML(code_html, html)

    def test_commodity_code_html_for_sub_heading(self):
        html = _commodity_code_html(self.subheading.commodity_code)
        code_html = """<span class="app-commodity-code app-hierarchy-tree__commodity-code" aria-label="Commodity code"><span class="app-commodity-code__highlight app-commodity-code__highlight--1">01</span><span class="app-commodity-code__highlight app-commodity-code__highlight--2">01</span><span class="app-commodity-code__highlight app-commodity-code__highlight--3">21</span><span class="app-commodity-code__highlight app-commodity-code__highlight--4"><span class="app-commodity-code__is-blank">00</span></span><span class="app-commodity-code__highlight app-commodity-code__highlight--5"><span class="app-commodity-code__is-blank">00</span></span></span>"""
        self.assertInHTML(code_html, html)

    def test_commodity_code_html_for_chapter(self):
        html = _commodity_code_html(self.chapter.chapter_code)
        code_html = """<span class="app-commodity-code app-hierarchy-tree__commodity-code" aria-label="Commodity code"><span class="app-commodity-code__highlight app-commodity-code__highlight--1">01</span><span class="app-commodity-code__highlight app-commodity-code__highlight--2"><span class="app-commodity-code__is-blank">00</span></span><span class="app-commodity-code__highlight app-commodity-code__highlight--3"><span class="app-commodity-code__is-blank">00</span></span><span class="app-commodity-code__highlight app-commodity-code__highlight--4"><span class="app-commodity-code__is-blank">00</span></span><span class="app-commodity-code__highlight app-commodity-code__highlight--5"><span class="app-commodity-code__is-blank">00</span></span></span>"""
        self.assertInHTML(code_html, html)


class MeasureConditionDetailTestCase(TestCase):

    """
    Test Measure Condition Detail View
    """

    def setUp(self):
        self.tree = create_nomenclature_tree(region='UK')

        self.commodity = mixer.blend(
            Commodity,
            commodity_code=settings.TEST_COMMODITY_CODE,
            goods_nomenclature_sid=12345,
            nomenclature_tree=self.tree,
        )
        self.commodity.tts_json = json.dumps(get_data(settings.COMMODITY_DATA))
        self.commodity.save_cache()

    fixtures = ["../../countries/fixtures/countries_data.json"]

    def test_commodity_has_tts_json(self):
        self.assertTrue(self.commodity.tts_obj)

    def test_commodity_json_has_measure_conditions(self):
        self.assertTrue("measure_conditions" in self.commodity.tts_json)

    def test_measure_condition_detail_http_status_is_200(self):
        resp = self.client.get(
            reverse(
                "commodity-measure-conditions",
                kwargs={
                    "commodity_code": settings.TEST_COMMODITY_CODE,
                    "country_code": settings.TEST_COUNTRY_CODE,
                    "nomenclature_sid": 12345,
                    "measure_id": 1,
                },
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_measure_condition_detail_with_nonexisting_country_code(self):
        resp = self.client.get(
            reverse(
                "commodity-measure-conditions",
                kwargs={
                    "commodity_code": settings.TEST_COMMODITY_CODE,
                    "country_code": "XY",
                    "nomenclature_sid": 12345,
                    "measure_id": 1,
                },
            )
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("choose-country"))

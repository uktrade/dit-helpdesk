import json
import logging
from datetime import datetime, timezone, timedelta

from django.apps import apps
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from mixer.backend.django import mixer

from commodities.models import Commodity
from commodities.views import commodity_hierarchy_context, _generate_commodity_code_html
from countries.models import Country
from hierarchy.models import Section, Chapter, Heading, SubHeading
from rules_of_origin.models import Rule, RulesGroup, RulesGroupMember, RulesDocument

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.DEBUG)

TEST_COMMODITY_CODE = "0101210000"
TEST_SUBHEADING_CODE = "0101210000"
TEST_HEADING_CODE = "0101000000"
TEST_CHAPTER_CODE = "0100000000"
TEST_SECTION_ID = "1"
TEST_COUNTRY_CODE = "AU"
TEST_COUNTRY_NAME = "Australia"

COMMODITY_DATA = settings.BASE_DIR + "/commodities/tests/commodity_{0}.json".format(TEST_COMMODITY_CODE)
COMMODITY_STRUCTURE = settings.BASE_DIR + "/commodities/tests/structure_{0}.json".format(TEST_COMMODITY_CODE)
SUBHEADING_STRUCTURE = settings.BASE_DIR + "/hierarchy/tests/subheading_{0}_structure.json".format(TEST_SUBHEADING_CODE)
HEADING_STRUCTURE = settings.BASE_DIR + "/hierarchy/tests/heading_{0}_structure.json".format(TEST_HEADING_CODE)
CHAPTER_STRUCTURE = settings.BASE_DIR + "/hierarchy/tests/chapter_{0}_structure.json".format(TEST_CHAPTER_CODE)
SECTION_STRUCTURE = settings.BASE_DIR + "/hierarchy/tests/section_{}_structure.json".format(TEST_SECTION_ID)


def get_data(file_path):
    with open(file_path) as f:
        json_data = json.load(f)
    return json_data


class CommodityViewTestCase(TestCase):

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
        self.section = self.create_instance(get_data(SECTION_STRUCTURE), 'hierarchy', 'Section')

        self.chapter = self.create_instance(get_data(CHAPTER_STRUCTURE), 'hierarchy', 'Chapter')
        self.chapter.section_id = self.section.pk
        self.chapter.save()

        self.heading = self.create_instance(get_data(HEADING_STRUCTURE), 'hierarchy', 'Heading')
        self.heading.chapter_id = self.chapter.id
        self.heading.save()

        self.subheading = self.create_instance(get_data(SUBHEADING_STRUCTURE), 'hierarchy', 'SubHeading')
        self.subheading.heading_id = self.heading.id
        self.subheading.save()

        self.commodity = self.create_instance(get_data(COMMODITY_STRUCTURE), 'commodities', 'Commodity')
        self.commodity.parent_subheading_id = self.subheading.id
        self.commodity.tts_json = json.dumps(get_data(COMMODITY_DATA))

        self.commodity.save()

        self.client = Client()
        self.url = reverse('commodity-detail', kwargs={"commodity_code": TEST_COMMODITY_CODE,
                                                       "country_code": TEST_COUNTRY_CODE})

    fixtures = ['../../countries/fixtures/countries_data.json']

    # fixtures = ['hierarchy/fixtures/hierarchy.json']
    # fixtures = ['commodities/fixtures/commodities.json']
    # fixtures = ['regulations/fixtures/regulations.json']

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

    def test_commodity_detail_view_is_using_the_correct_template(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed('commodity_detail.html')
        self.assertInHTML(
            resp.context['commodity'].description,
            resp.content.decode("utf-8")
        )

    def test_commodity_detail_receives_the_correct_country_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.context['selected_origin_country'], TEST_COUNTRY_CODE)

    def test_commodity_detail_has_the_correct_commodity_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.context['commodity'].commodity_code, TEST_COMMODITY_CODE)

    def test_commodity_detail_has_the_selected_country_origin_name(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.context['selected_origin_country_name'], TEST_COUNTRY_NAME)

    def test_commodity_column_titles_are_correct(self):
        resp = self.client.get(self.url)
        self.assertEqual(
            resp.context['column_titles'],
            ['Country', 'Measure type', 'Value', 'Conditions', 'Excluded countries', 'Date']
        )

    def test_commodity_detail_without_country_code(self):
        self.assertRaises(NoReverseMatch, lambda: self.client.get(reverse('commodity-detail'),
                                                                  kwargs={"commodity_code": TEST_COMMODITY_CODE}))

    def test_commodity_detail_without_commodity_code(self):
        self.assertRaises(NoReverseMatch, lambda: self.client.get(reverse('commodity-detail'),
                                                                  kwargs={"country_code": TEST_COUNTRY_CODE}))

    def test_commodity_detail_with_nonexisting_country_code(self):
        resp = self.client.get(reverse('commodity-detail', kwargs={"commodity_code": TEST_COMMODITY_CODE,
                                                                   "country_code": "XY"}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, "/choose-country/")

    def test_commodity_detail_update(self):
        commodity = Commodity.objects.get(commodity_code=TEST_COMMODITY_CODE)
        commodity.tts_json = None
        commodity.save()
        resp = self.client.get(reverse('commodity-detail', kwargs={"commodity_code": TEST_COMMODITY_CODE,
                                                                   "country_code": TEST_COUNTRY_CODE}))
        self.assertEqual(resp.status_code, 200)
        logger.info(commodity.last_updated.toordinal())
        logger.info(datetime.now(timezone.utc).toordinal())

        self.assertAlmostEqual(commodity.last_updated.toordinal(), datetime.now(timezone.utc).toordinal())

    def test_commodity_detail_with_rules_or_origin(self):
        rules_group = mixer.blend(
            RulesGroup,
            description="test rules group"
        )
        rules_group_member = mixer.blend(
            RulesGroupMember,
            rules_group=rules_group,
            country=Country.objects.get(country_code="AF")
        )
        rules_document = mixer.blend(
            RulesDocument,
            description="test rules document",
            rules_group=rules_group
        )

        rule = mixer.blend(
            Rule,
            rules_document=rules_document,
            chapter=self.chapter
        )
        resp = self.client.get(reverse('commodity-detail', kwargs={"commodity_code": TEST_COMMODITY_CODE,
                                                                   "country_code": "AF"}))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('rules_of_origin' in resp.context)
        self.assertTrue(resp.context['rules_of_origin'])

    def test_commodity_hierarchy_context(self):
        html = commodity_hierarchy_context(self.commodity.get_path(), TEST_COUNTRY_CODE, self.commodity.commodity_code)
        self.assertInHTML("Live animals" and
                          "Live horses, asses, mules and hinnies" and
                          "Horses" and
                          "Pure-bred breeding animals", html)

    def test_generate_commodity_code_html_for_commodity(self):
        html = _generate_commodity_code_html(self.commodity)
        logger.info(self.commodity)
        logger.info(html)
        self.assertInHTML('010121', html)

    def test_generate_commodity_code_html_for_section(self):
        html = _generate_commodity_code_html(self.section)
        logger.info(self.section)
        logger.info(html)
        self.assertEqual(html, '')

    def test_generate_commodity_code_html_for_heading(self):
        html = _generate_commodity_code_html(self.heading)
        logger.info(self.heading)
        logger.info(html)
        self.assertInHTML('010100', html)

    def test_generate_commodity_code_html_for_sub_heading(self):
        html = _generate_commodity_code_html(self.subheading)
        logger.info(self.subheading)
        logger.info(html)
        self.assertInHTML('010121', html)

    def test_generate_commodity_code_html_for_chapter(self):
        html = _generate_commodity_code_html(self.chapter)
        logger.info(self.chapter)
        logger.info(html)
        self.assertInHTML('010000', html)


class MeasureConditionDetailTestCase(TestCase):

    def setUp(self):
        self.commodity = mixer.blend(
            Commodity,
            commodity_code=TEST_COMMODITY_CODE,
            tts_json=json.dumps(get_data(COMMODITY_DATA))
        )

    fixtures = ['../../countries/fixtures/countries_data.json']

    def test_commodity_has_tts_json(self):
        logger.info(self.commodity.tts_obj.get_import_measure_by_id(int(1), country_code=TEST_COUNTRY_CODE))
        self.assertTrue(self.commodity.tts_obj)

    def test_commodity_json_has_measure_conditions(self):
        self.assertTrue("measure_conditions" in self.commodity.tts_json)

    def test_measure_condition_detail_http_status_is_200(self):
        resp = self.client.get(reverse('commodity-measure-conditions',
                                       kwargs={"commodity_code": TEST_COMMODITY_CODE,
                                               "country_code": TEST_COUNTRY_CODE,
                                               "measure_id": 1}))
        self.assertEqual(resp.status_code, 200)

    def test_measure_condition_detail_with_nonexisting_country_code(self):
        resp = self.client.get(reverse('commodity-measure-conditions',
                                       kwargs={"commodity_code": TEST_COMMODITY_CODE,
                                               "country_code": "XY",
                                               "measure_id": 1}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, "/choose-country/")

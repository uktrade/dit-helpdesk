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
logger.setLevel(logging.INFO)


def get_data(file_path):
    with open(file_path) as f:
        json_data = json.load(f)
    return json_data


class CommodityViewTestCase(TestCase):

    """
    Test Commodity View
    """

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
        self.section = self.create_instance(get_data(settings.SECTION_STRUCTURE), 'hierarchy', 'Section')

        self.chapter = self.create_instance(get_data(settings.CHAPTER_STRUCTURE), 'hierarchy', 'Chapter')
        self.chapter.section_id = self.section.pk
        self.chapter.save()

        self.heading = self.create_instance(get_data(settings.HEADING_STRUCTURE), 'hierarchy', 'Heading')
        self.heading.chapter_id = self.chapter.id
        self.heading.save()

        self.subheading = self.create_instance(get_data(settings.SUBHEADING_STRUCTURE), 'hierarchy', 'SubHeading')
        self.subheading.heading_id = self.heading.id
        self.subheading.save()

        self.commodity = self.create_instance(get_data(settings.COMMODITY_STRUCTURE), 'commodities', 'Commodity')
        self.commodity.parent_subheading_id = self.subheading.id
        self.commodity.tts_json = json.dumps(get_data(settings.COMMODITY_DATA))

        self.commodity.save()

        self.client = Client()
        self.url = reverse('commodity-detail', kwargs={"commodity_code": settings.TEST_COMMODITY_CODE,
                                                       "country_code": settings.TEST_COUNTRY_CODE})

    fixtures = [settings.COUNTRIES_DATA]

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
        self.assertTemplateUsed(resp, 'commodity_detail.html')
        self.assertInHTML(
            resp.context['commodity'].description,
            resp.content.decode("utf-8")
        )

    def test_commodity_detail_receives_the_correct_country_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.context['selected_origin_country'], settings.TEST_COUNTRY_CODE)

    def test_commodity_detail_has_the_correct_commodity_code(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.context['commodity'].commodity_code, settings.TEST_COMMODITY_CODE)

    def test_commodity_detail_has_the_selected_country_origin_name(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.context['selected_origin_country_name'], settings.TEST_COUNTRY_NAME)

    def test_commodity_column_titles_are_correct(self):
        resp = self.client.get(self.url)
        self.assertEqual(
            resp.context['column_titles'],
            ['Country', 'Measure type', 'Value', 'Conditions', 'Excluded countries', 'Date']
        )

    def test_commodity_detail_without_country_code(self):
        self.assertRaises(NoReverseMatch, lambda: self.client.get(reverse('commodity-detail'),
                                                                  kwargs={"commodity_code": settings.TEST_COMMODITY_CODE}))

    def test_commodity_detail_without_commodity_code(self):
        self.assertRaises(NoReverseMatch, lambda: self.client.get(reverse('commodity-detail'),
                                                                  kwargs={"country_code": settings.TEST_COUNTRY_CODE}))

    def test_commodity_detail_with_nonexisting_country_code(self):
        resp = self.client.get(reverse('commodity-detail', kwargs={"commodity_code": settings.TEST_COMMODITY_CODE,
                                                                   "country_code": "XY"}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, "/choose-country/")

    def test_commodity_detail_update(self):
        commodity = Commodity.objects.get(commodity_code=settings.TEST_COMMODITY_CODE)
        commodity.tts_json = None
        commodity.save()
        resp = self.client.get(reverse('commodity-detail', kwargs={"commodity_code": settings.TEST_COMMODITY_CODE,
                                                                   "country_code": settings.TEST_COUNTRY_CODE}))
        self.assertEqual(resp.status_code, 200)
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
        resp = self.client.get(reverse('commodity-detail', kwargs={"commodity_code": settings.TEST_COMMODITY_CODE,
                                                                   "country_code": "AF"}))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('rules_of_origin' in resp.context)
        self.assertTrue(resp.context['rules_of_origin'])

    def test_commodity_hierarchy_context(self):
        html = commodity_hierarchy_context(self.commodity.get_path(), settings.TEST_COUNTRY_CODE,
                                           self.commodity.commodity_code)
        self.assertInHTML("Live animals" and
                          "Live horses, asses, mules and hinnies" and
                          "Horses" and
                          "Pure-bred breeding animals", html)

    def test_generate_commodity_code_html_for_commodity(self):
        html = _generate_commodity_code_html(self.commodity)
        self.assertInHTML('010121', html)

    def test_generate_commodity_code_html_for_section(self):
        html = _generate_commodity_code_html(self.section)
        self.assertEqual(html, '')

    def test_generate_commodity_code_html_for_heading(self):
        html = _generate_commodity_code_html(self.heading)
        self.assertInHTML('010100', html)

    def test_generate_commodity_code_html_for_sub_heading(self):
        html = _generate_commodity_code_html(self.subheading)
        self.assertInHTML('010121', html)

    def test_generate_commodity_code_html_for_chapter(self):
        html = _generate_commodity_code_html(self.chapter)
        self.assertInHTML('010000', html)


class MeasureConditionDetailTestCase(TestCase):

    """
    Test Measure Condition Detail View
    """

    def setUp(self):
        self.commodity = mixer.blend(
            Commodity,
            commodity_code=settings.TEST_COMMODITY_CODE,
            tts_json=json.dumps(get_data(settings.COMMODITY_DATA))
        )

    fixtures = ['../../countries/fixtures/countries_data.json']

    def test_commodity_has_tts_json(self):
        self.assertTrue(self.commodity.tts_obj)

    def test_commodity_json_has_measure_conditions(self):
        self.assertTrue("measure_conditions" in self.commodity.tts_json)

    def test_measure_condition_detail_http_status_is_200(self):
        resp = self.client.get(reverse('commodity-measure-conditions',
                                       kwargs={"commodity_code": settings.TEST_COMMODITY_CODE,
                                               "country_code": settings.TEST_COUNTRY_CODE,
                                               "measure_id": 1}))
        self.assertEqual(resp.status_code, 200)

    def test_measure_condition_detail_with_nonexisting_country_code(self):
        resp = self.client.get(reverse('commodity-measure-conditions',
                                       kwargs={"commodity_code": settings.TEST_COMMODITY_CODE,
                                               "country_code": "XY",
                                               "measure_id": 1}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, "/choose-country/")

import json
import logging

from django.apps import apps
from django.conf import settings
from django.test import TestCase, Client

from commodities.models import Commodity
from countries.models import Country
from hierarchy.models import Section, Chapter, Heading, SubHeading
from hierarchy.views import _get_expanded_context

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)

TEST_COMMODITY_CODE = "0101210000"
TEST_SUBHEADING_CODE = "0101210000"


def create_instance(data, app_name, model_name):

    model = apps.get_model(app_label=app_name, model_name=model_name)
    instance = model(**data)
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
        self.section = create_instance(get_data(settings.SECTION_STRUCTURE), 'hierarchy', 'Section')

        self.chapter = create_instance(get_data(settings.CHAPTER_STRUCTURE), 'hierarchy', 'Chapter')
        self.chapter.section_id = self.section.pk
        self.chapter.save()

        self.heading = create_instance(get_data(settings.HEADING_STRUCTURE), 'hierarchy', 'Heading')
        self.heading.chapter_id = self.chapter.pk
        self.heading.save()

        self.subheading = create_instance(get_data(settings.SUBHEADING_STRUCTURE), 'hierarchy', 'SubHeading')
        self.subheading.heading_id = self.heading.id
        self.subheading.save()

        self.commodity = create_instance(get_data(settings.COMMODITY_STRUCTURE), 'commodities', 'Commodity')
        self.commodity.parent_subheading_id = self.subheading.id
        self.commodity.tts_json = json.dumps(get_data(settings.COMMODITY_DATA))

        self.commodity.save()

        self.client = Client()

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

    def test_hierarchy_data_is_valid(self):
        response = self.client.get('/search/country/au/hierarchy/root')
        self.assertEqual(response.status_code, 200)

    def test_hierarchy_data_at_root(self):
        response = self.client.get('/search/country/au/hierarchy/root')
        self.assertInHTML("Live animals; animal products", response.context['hierarchy_html'])
        self.assertEqual(response.context['country_code'], settings.TEST_COUNTRY_CODE.lower())

    def test_hierarchy_data_at_section(self):
        response = self.client.get('/search/country/au/hierarchy/section-2#section-2')
        self.assertInHTML(settings.TEST_SECTION_DESCRIPTION, response.context['hierarchy_html'])
        self.assertEqual(response.context['country_code'], settings.TEST_COUNTRY_CODE.lower())

    def test_hierarchy_data_at_chapter(self):
        chapter_id = Chapter.objects.get(chapter_code=settings.TEST_CHAPTER_CODE).pk
        response = self.client.get('/search/country/au/hierarchy/chapter-{0}#chapter-{0}'.format(chapter_id))
        logger.debug(response.context['hierarchy_html'])
        self.assertInHTML(settings.TEST_SECTION_DESCRIPTION, response.context['hierarchy_html'])
        self.assertInHTML(settings.TEST_CHAPTER_DESCRIPTION, response.context['hierarchy_html'])
        self.assertEqual(response.context['country_code'], settings.TEST_COUNTRY_CODE.lower())

    def test_hierarchy_data_at_heading(self):
        heading_id = Heading.objects.get(heading_code=settings.TEST_HEADING_CODE).pk
        response = self.client.get('/search/country/au/hierarchy/heading-{0}#heading-{0}'.format(heading_id))
        self.assertInHTML(settings.TEST_SECTION_DESCRIPTION, response.context['hierarchy_html'])
        self.assertInHTML(settings.TEST_CHAPTER_DESCRIPTION, response.context['hierarchy_html'])
        self.assertInHTML(settings.TEST_HEADING_DESCRIPTION, response.context['hierarchy_html'])
        self.assertEqual(response.context['country_code'], settings.TEST_COUNTRY_CODE.lower())

    def test_hierarchy_data_at_subheading(self):
        subheading_id = SubHeading.objects.get(commodity_code=TEST_SUBHEADING_CODE).pk
        response = self.client.get('/search/country/au/hierarchy/sub_heading-{0}#sub_heading-{0}'.format(subheading_id))
        self.assertInHTML(settings.TEST_SECTION_DESCRIPTION, response.context['hierarchy_html'])
        self.assertInHTML(settings.TEST_CHAPTER_DESCRIPTION, response.context['hierarchy_html'])
        self.assertInHTML(settings.TEST_HEADING_DESCRIPTION, response.context['hierarchy_html'])
        self.assertInHTML(settings.TEST_SUBHEADING_DESCRIPTION, response.context['hierarchy_html'])
        self.assertEqual(response.context['country_code'], settings.TEST_COUNTRY_CODE.lower())

    def test_expanded_context_with_subheading_node(self):
        subheading_id = SubHeading.objects.get(commodity_code=settings.TEST_SUBHEADING_CODE).pk
        node_id = '#sub_heading-{0}'.format(subheading_id)
        logger.debug(_get_expanded_context(node_id))
        self.assertFalse(_get_expanded_context(node_id))


def get_data(file_path):

    with open(file_path) as f:
        json_data = json.load(f)
    return json_data

import json

from django.apps import apps
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse

from commodities.models import Commodity
from countries.models import Country
from hierarchy.models import Section, Chapter, Heading, SubHeading

TEST_COMMODITY_CODE = "0101210000"
TEST_SUBHEADING_CODE = "0101210000"
TEST_HEADING_CODE = "0101000000"
TEST_CHAPTER_CODE = "0100000000"
TEST_SECTION_ID = "1"
TEST_COUNTRY_CODE = "AU"
TEST_COUNTRY_NAME = "Australia"

COMMODITY_DATA = settings.BASE_DIR+"/commodities/tests/commodity_{0}.json".format(TEST_COMMODITY_CODE)
COMMODITY_STRUCTURE = settings.BASE_DIR+"/commodities/tests/structure_{0}.json".format(TEST_COMMODITY_CODE)
SUBHEADING_STRUCTURE = settings.BASE_DIR+"/hierarchy/tests/subheading_{0}_structure.json".format(TEST_SUBHEADING_CODE)
HEADING_STRUCTURE = settings.BASE_DIR+"/hierarchy/tests/heading_{0}_structure.json".format(TEST_HEADING_CODE)
CHAPTER_STRUCTURE = settings.BASE_DIR+"/hierarchy/tests/chapter_{0}_structure.json".format(TEST_CHAPTER_CODE)
SECTION_STRUCTURE = settings.BASE_DIR+"/hierarchy/tests/section_{}_structure.json".format(TEST_SECTION_ID)


class CommodityViewTestCase(TestCase):

    def get_data(self, file_path):

        with open(file_path) as f:
            json_data = json.load(f)
        return json_data

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
        self.section = self.create_instance(self.get_data(SECTION_STRUCTURE), 'hierarchy', 'Section')

        self.chapter = self.create_instance(self.get_data(CHAPTER_STRUCTURE), 'hierarchy', 'Chapter')
        self.chapter.parent = self.section.pk
        self.chapter.save()

        self.heading = self.create_instance(self.get_data(HEADING_STRUCTURE), 'hierarchy', 'Heading')
        self.heading.chapter_id = self.heading.pk
        self.heading.save()

        self.subheading = self.create_instance(self.get_data(SUBHEADING_STRUCTURE), 'hierarchy', 'SubHeading')
        self.subheading.heading_id = self.heading.id
        self.subheading.save()

        self.commodity = self.create_instance(self.get_data(COMMODITY_STRUCTURE), 'commodities', 'Commodity')
        self.commodity.parent_subheading_id = self.subheading.id
        self.commodity.tts_json = json.dumps(self.get_data(COMMODITY_DATA))

        self.commodity.save()

        self.client = Client()
        self.url = reverse('commodity-detail', kwargs={"commodity_code": TEST_COMMODITY_CODE,
                                                       "country_code": TEST_COUNTRY_CODE})

    fixtures = ['countries/fixtures/countries_data.json']
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
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_commodity_detail_view_is_using_the_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed('commodity_detail.html')
        self.assertInHTML(
            response.context['commodity'].description,
            response.content.decode("utf-8")
        )

    def test_commodity_detail_receives_the_correct_country_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['selected_origin_country'], TEST_COUNTRY_CODE)

    def test_commodity_detail_has_the_correct_commodity_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['commodity'].commodity_code, TEST_COMMODITY_CODE)

    def test_commodity_detail_has_the_selected_country_origin_name(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['selected_origin_country_name'], TEST_COUNTRY_NAME)

    def test_commodity_column_titles_are_correct(self):
        response = self.client.get(self.url)
        self.assertEqual(
            response.context['column_titles'],
            ['Country', 'Description', 'Conditions', 'Value', 'Excluded Countries', 'Date', 'Legal Base', 'Footnotes']
        )
import json

from django.apps import apps
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse


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


class SearchViewTestCase(TestCase):

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

        # self.url = reverse('search-view')

    def test_search_hierachy_view_is_using_the_correct_template(self):
        response = self.client.get(reverse('search-hierarchy',
                                           kwargs={"country_code": TEST_COUNTRY_CODE, "node_id": "section-1"}))
        self.assertTemplateUsed(response, 'search/commodity_search.html')

    def test_search_hierachy_view_(self):
        response = self.client.get(reverse('search-hierarchy',
                                           kwargs={"country_code": TEST_COUNTRY_CODE}))
        print(response.context)
        self.assertTemplateUsed('search/commodity_search.html')

    def test_search_view_redirects_to_choose_country(self):
        response = self.client.get(reverse('search-view'))
        self.assertRedirects(response, '/choose-country/')


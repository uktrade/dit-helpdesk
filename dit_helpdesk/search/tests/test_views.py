import logging

from django.conf import settings
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from mixer.backend.django import mixer
from model_mommy.recipe import seq

from commodities.models import Commodity
from hierarchy.models import Section, Chapter, Heading, ROMAN_NUMERALS, SubHeading
from search.views import CommoditySearchView

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class CommoditySearchViewTestCase(TestCase):

    """
    Test Search view
    """

    def setUp(self):
        self.section = mixer.blend(
            Section,
            section_id=10,
            roman_numeral=ROMAN_NUMERALS[1],
            tts_json="{}"
        )
        """create three chapters starting at 47 and attach to section 10"""
        self.chapters = mixer.cycle(3).blend(
            Chapter,
            tts_json="{}",
            section=self.section,
            chapter_code=seq(46)
        )
        """create 11 headings starting at 4901 and attached to chapter 49"""
        self.headings = mixer.cycle(11).blend(
            Heading,
            chapter=self.chapters[2],
            heading_code=(x for x in [4901000000, 4902000000, 4903000000, 4904000000, 4905000000, 4906000000,
                                      4907000000, 4908000000, 4909000000, 4910000000, 4911000000])
        )
        """create 6 subheadings starting at 4901 attached to heading 4901"""
        self.parent_subheadings = mixer.cycle(6).blend(
            SubHeading,
            heading=self.headings[0],
            commodity_code=(x for x in [4901000000, 4902000000, 4905000000, 4907000000, 4908000000, 4911000000])
        )
        """create 2 subheadings attached to subheading 4911"""
        self.subheadings = mixer.cycle(2).blend(
            SubHeading,
            parent_subheading=self.parent_subheadings[5],
            commodity_code=(x for x in [4911100000, 4911910000])
        )
        """create 1 subheading attached to subheading 491191"""
        self.sub_subheadings = mixer.cycle(1).blend(
            SubHeading,
            parent_subheading=self.subheadings[1],
            commodity_code=4911910000
        )
        """create 3 commodites attached to """
        self.commodities = mixer.cycle(3).blend(
            Commodity,
            parent_subheading=self.sub_subheadings[0],
            commodity_code=(x for x in [4911910010, 4911910090, 4911990000])
        )
        self.client = Client()


    fixtures = [settings.COUNTRIES_DATA]

    def test_section_1_exists(self):
        self.assertTrue(Section.objects.filter(section_id=10).exists())

    def test_3_chapters_exist(self):
        self.assertEqual(len(Chapter.objects.all()), 3)

    def test_11_headings_exist(self):
        self.assertEqual(len(Heading.objects.all()), 11)

    def test_3_headings_exist(self):
        self.assertEqual(len(SubHeading.objects.all()), 9)

    def test_3_commodities_exist(self):
        self.assertEqual(len(Commodity.objects.all()), 3)

    def test_commodity_search_is_using_the_correct_template(self):
        logger.info(reverse('search-view', kwargs={"country_code": "au"}))
        response = self.client.get(reverse('search-view', kwargs={"country_code": "au"}))
        self.assertTemplateUsed(response, 'search/commodity_search.html')


    # def test_search_view_returns_http_200(self):
    #     resp = self.client.get(reverse('search-view', kwargs={"country_code": "au"}))
    #     self.assertEqual(resp.status_code, 200)
    #
    # def test_search_view_with_nonexisting_country_code_returns_http_302(self):
    #     resp = self.client.get(reverse('search', kwargs={"country_code": "XY"}))
    #     self.assertEqual(resp.status_code, 302)

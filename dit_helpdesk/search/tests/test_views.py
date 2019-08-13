import logging

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from mixer.backend.django import mixer


from commodities.models import Commodity
from hierarchy.models import Section, Chapter, Heading, ROMAN_NUMERALS, SubHeading
from hierarchy.views import _get_hierarchy_level_html
from search.forms import CommoditySearchForm
from search.views import search_hierarchy, process_commodity_code, _generate_commodity_code_html

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class CommoditySearchViewTestCase(TestCase):

    """
    Test Commodity code Search view
    """

    def setUp(self):
        self.section = mixer.blend(
            Section,
            section_id=10,
            title=settings.TEST_SECTION_DESCRIPTION,
            roman_numeral=ROMAN_NUMERALS[1],
            tts_json="{}",
            commodity_code=10
        )
        """create three chapters starting at 47 and attach to section 10"""
        self.chapters = mixer.cycle(3).blend(
            Chapter,
            tts_json="{}",
            section=self.section,
            chapter_code=(x for x in [4700000000, 4800000000, 4900000000]),
            goods_nomenclature_sid=(x for x in [4700000000, 4800000000, 4900000000])
        )
        """create 11 headings starting at 4901 and attached to chapter 49"""
        self.headings = mixer.cycle(11).blend(
            Heading,
            chapter=self.chapters[2],
            heading_code=(x for x in [4901000000, 4902000000, 4903000000, 4904000000, 4905000000, 4906000000,
                                      4907000000, 4908000000, 4909000000, 4910000000, 4911000000]),
            goods_nomenclature_sid=(x for x in [4901000000, 4902000000, 4903000000, 4904000000, 4905000000, 4906000000,
                                      4907000000, 4908000000, 4909000000, 4910000000, 4911000000]),
        )
        """create 6 subheadings starting at 4901 attached to heading 4901"""
        self.parent_subheadings = mixer.cycle(6).blend(
            SubHeading,
            heading=self.headings[0],
            commodity_code=(x for x in [4901000000, 4902000000, 4905000000, 4907000000, 4908000000, 4911000000]),
            goods_nomenclature_sid=(x for x in [4901000000, 4902000000, 4905000000, 4907000000, 4908000000, 4911000000]),
        )
        """create 2 subheadings attached to subheading 4911"""
        self.subheadings = mixer.cycle(2).blend(
            SubHeading,
            parent_subheading=self.parent_subheadings[5],
            commodity_code=(x for x in [4911100000, 4911910000]),
            goods_nomenclature_sid=(x for x in [4911100000, 4911910000]),
        )
        """create 1 subheading attached to subheading 491191"""
        self.sub_subheadings = mixer.cycle(1).blend(
            SubHeading,
            parent_subheading=self.subheadings[1],
            commodity_code=4911910000,
            goods_nomenclature_sid=4911910000,
        )
        """create 3 commodites attached to """
        self.commodities = mixer.cycle(3).blend(
            Commodity,
            parent_subheading=self.sub_subheadings[0],
            commodity_code=(x for x in [4911910010, 4911910090, 4911990000]),
            goods_nomenclature_sid=(x for x in [4911910010, 4911910090, 4911990000]),
            description=(x for x in ["Paper", "Scissors", "Rock"])
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
        url = reverse('search:search-commodity', kwargs={"country_code": "au"})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'search/commodity_search.html')

    def test_search_view_returns_http_200(self):
        resp = self.client.get(reverse('search:search-commodity', kwargs={"country_code": "au"}))
        self.assertEqual(resp.status_code, 200)

    def test_search_view_with_code_the_form_is_valid_is_redirected(self):
        url = reverse("search:search-commodity", kwargs={"country_code": "au"})
        data = {"q": '4901', "country": "au"}
        resp = self.client.get(url, data=data, follow=False)
        self.assertEqual(resp.status_code, 302)

    def test_search_view_with_code__the_form_is_valid_follow_is_ok(self):
        url = reverse("search:search-commodity", kwargs={"country_code": "au"})
        data = {"q": "4911910010", "country": "au"}
        resp = self.client.get(url, data=data, follow=True)
        self.assertEqual(resp.status_code, 200)


class SearchFormTestCase(TestCase):

    def test_form_is_valid_with_a_query(self):
        form_data = {'q': 'Paper', 'country': 'AU'}
        form = CommoditySearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_is_not_valid_with_missing_query(self):
        form_data = {'q': '', 'country': 'AU'}
        form = CommoditySearchForm(data=form_data)
        self.assertFalse(form.is_valid())


class CommodityKeywordSearchViewTestCase(TestCase):
    #     """
    #     Test Keyword Search view
    #     """

    def setUp(self):
        self.client = Client()

    fixtures = [settings.COUNTRIES_DATA]

    def test_commodity_keyword_search_has_query(self):
        path = reverse("search:search-commodity", kwargs={"country_code": "au"})
        resp = self.client.get(path, data={"q": "Paper", "country": "au"})
        self.assertIn("q", resp.request["QUERY_STRING"])

    def test_commodity_keyword_search_query_is_empty(self):
        resp = self.client.get(reverse("search:search-commodity", kwargs={"country_code": "au"}),
                               data={"q": "", "country": "au"})
        self.assertEqual(resp.context['form'].is_valid(), False)

    def test_commodity_keyword_search_query_context_has_correct_country(self):
        resp = self.client.get(reverse("search:search-commodity", kwargs={"country_code": "au"}),
                               data={"q": "Paper", "country": "au"})
        self.assertEqual(resp.context['selected_origin_country_name'], "Australia")

    def test_commodity_keyword_search_query_is_using_the_correct_form(self):
        resp = self.client.get(reverse("search:search-commodity", kwargs={"country_code": "au"}),
                               data={"q": "Paper", "country": "au"})
        self.assertIsInstance(resp.context['form'], CommoditySearchForm)

    def test_commodity_keyword_search_query_is_at_page_one(self):
        resp = self.client.get(reverse("search:search-commodity", kwargs={"country_code": "au"}),
                               data={"q": "Paper", "country": "au"})
        self.assertEqual(resp.context['form'].is_valid(), True)


class ProcessCommodityCodeTestCase(TestCase):

    """
    Test Process Commodity Code
    """

    def test_process_commodity_code_for_single_digit_entered(self):
        code = process_commodity_code("2")
        self.assertEqual(code, "0200000000")

    def test_process_commodity_code_for_00_digit_entered(self):
        code = process_commodity_code("00")
        self.assertEqual(code, "9999000000")

    def test_process_commodity_code_for_99_digit_entered(self):
        code = process_commodity_code("99")
        self.assertEqual(code, "9999000000")

    def test_process_commodity_code_for_two_digits_entered(self):
        code = process_commodity_code("21")
        self.assertEqual(code, "2100000000")

    def test_process_commodity_code_for_four_digits_ending_with_00_entered(self):
        code = process_commodity_code("2100")
        self.assertEqual(code, "2100000000")

    def test_process_commodity_code_for_four_digits_entered(self):
        code = process_commodity_code("4104")
        self.assertEqual(code, "4104000000")

    def test_process_commodity_code_for_six_digits_ending_with_0000_entered(self):
        code = process_commodity_code("210000")
        self.assertEqual(code, "2100000000")

    def test_process_commodity_code_for_six_digits_entered(self):
        code = process_commodity_code("410411")
        self.assertEqual(code, "4104110000")

    def test_process_commodity_code_for_eight_digits_entered(self):
        code = process_commodity_code("41041159")
        self.assertEqual(code, "4104115900")

    def test_process_commodity_code_for_three_digits_entered(self):
        code = process_commodity_code("410")
        self.assertEqual(code, "4100000000")

    def test_process_commodity_code_for_five_digits_entered(self):
        code = process_commodity_code("41012")
        self.assertEqual(code, "4101000000")

    def test_process_commodity_code_for_seven_digits_entered(self):
        code = process_commodity_code("4101203")
        self.assertEqual(code, "4101200000")

    def test_process_commodity_code_for_nine_digits_entered(self):
        code = process_commodity_code("410411510")
        self.assertEqual(code, "4104115100")

    def test_process_commodity_code_for_ten_digits_entered(self):
        code = process_commodity_code("4104115900")
        self.assertEqual(code, "4104115900")

    def test_process_commodity_code_for_greater_than_10_digits_entered(self):
        code = process_commodity_code("410411590123")
        self.assertEqual(code, "4104115900")


class GenerateCommodityCodeHTMLTestCase(TestCase):
    """
    Test Generate commodity code HTML
    """
    def test_generate_commodity_code_html(self):
        code = _generate_commodity_code_html("4104115900")
        self.assertEqual(code, '<span class="app-commodity-code app-hierarchy-tree__commodity-code"><span '
                               'class="app-commodity-code__highlight app-commodity-code__highlight--1">41</span><span '
                               'class="app-commodity-code__highlight app-commodity-code__highlight--2">04</span><span '
                               'class="app-commodity-code__highlight '
                               'app-commodity-code__highlight--3">115900</span></span>')


class TestSearchHierarchyTestCase(TestCase):
    """
    Test search hierarchy view
    """
    def setUp(self):

        self.client = Client()

    fixtures = [settings.COUNTRIES_DATA]

    def test_search_hierarchy(self):
        request = RequestFactory().get(reverse("search:search-hierarchy",
                                               kwargs={"country_code": "au", "node_id": "section-1"}))
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session["origin_country"] = "au"
        request.session.save()

        resp = search_hierarchy(request=request, node_id="section-1", country_code="au")
        self.assertEqual(resp.status_code, 200)

    def test__get_hierarchy_level_html(self):
        resp = _get_hierarchy_level_html('root', ['section-1'], 'au')
        self.assertIn('class="app-hierarchy-tree"', format(resp))

    def test_search_hierarchy_when_country_code_is_None(self):
        request = RequestFactory().get(reverse("search:search-hierarchy",
                                               kwargs={"country_code": "au", "node_id": "section-1"}))
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session["origin_country"] = None
        request.session.save()

        resp = search_hierarchy(request=request, node_id="section-1", country_code=None)
        self.assertEqual(resp.status_code, 302)
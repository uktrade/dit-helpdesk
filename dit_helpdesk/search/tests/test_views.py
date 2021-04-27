import json
import logging

from unittest import mock

from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from mixer.backend.django import mixer

from commodities.models import Commodity
from hierarchy.models import Section, Chapter, Heading, SubHeading
from hierarchy.helpers import create_nomenclature_tree
from hierarchy.views import _commodity_code_html
from search.forms import CommoditySearchForm
from search.views import search_hierarchy
from search.helpers import process_commodity_code

from search.documents.section import INDEX as section_index
from search.documents.chapter import INDEX as chapter_index
from search.documents.heading import INDEX as heading_index
from search.documents.subheading import INDEX as sub_heading_index
from search.documents.commodity import INDEX as commodity_index

indices = [
    section_index,
    chapter_index,
    heading_index,
    sub_heading_index,
    commodity_index,
]


logger = logging.getLogger(__name__)


class CommoditySetupTestCase(TestCase):
    def setUp(self):
        self.tree = create_nomenclature_tree("UK")
        self.section = mixer.blend(
            Section,
            section_id=10,
            title=settings.TEST_SECTION_DESCRIPTION,
            roman_numeral="X",
            tts_json="{}",
            nomenclature_tree=self.tree,
        )
        """create three chapters starting at 47 and attach to section 10"""
        self.chapters = mixer.cycle(3).blend(
            Chapter,
            tts_json="{}",
            section=self.section,
            chapter_code=(x for x in [4700000000, 4800000000, 4900000000]),
            goods_nomenclature_sid=(x for x in [4700000000, 4800000000, 4900000000]),
            nomenclature_tree=self.tree,
        )
        """create 11 headings starting at 4901 and attached to chapter 49"""
        self.headings = mixer.cycle(11).blend(
            Heading,
            chapter=self.chapters[2],
            heading_code=(
                x
                for x in [
                    4901000000,
                    4902000000,
                    4903000000,
                    4904000000,
                    4905000000,
                    4906000000,
                    4907000000,
                    4908000000,
                    4909000000,
                    4910000000,
                    4911000000,
                ]
            ),
            goods_nomenclature_sid=(
                x
                for x in [
                    4901000000,
                    4902000000,
                    4903000000,
                    4904000000,
                    4905000000,
                    4906000000,
                    4907000000,
                    4908000000,
                    4909000000,
                    4910000000,
                    4911000000,
                ]
            ),
            nomenclature_tree=self.tree,
        )
        """create 6 subheadings starting at 4901 attached to heading 4901"""
        self.parent_subheadings = mixer.cycle(6).blend(
            SubHeading,
            heading=self.headings[0],
            commodity_code=(
                x
                for x in [
                    4901000000,
                    4902000000,
                    4905000000,
                    4907000000,
                    4908000000,
                    4911000000,
                ]
            ),
            goods_nomenclature_sid=(
                x
                for x in [
                    4901000000,
                    4902000000,
                    4905000000,
                    4907000000,
                    4908000000,
                    4911000000,
                ]
            ),
            nomenclature_tree=self.tree,
        )
        """create 2 subheadings attached to subheading 4911"""
        self.subheadings = mixer.cycle(2).blend(
            SubHeading,
            parent_subheading=self.parent_subheadings[5],
            commodity_code=(x for x in [4911100000, 4911910000]),
            goods_nomenclature_sid=(x for x in [4911100000, 4911910000]),
            nomenclature_tree=self.tree,
        )
        """create 1 subheading attached to subheading 491191"""
        self.sub_subheadings = mixer.cycle(1).blend(
            SubHeading,
            parent_subheading=self.subheadings[1],
            commodity_code=4911910000,
            goods_nomenclature_sid=4911910000,
            nomenclature_tree=self.tree,
        )
        """create 3 commodites attached to """
        self.commodities = mixer.cycle(3).blend(
            Commodity,
            parent_subheading=self.sub_subheadings[0],
            commodity_code=(x for x in [4911910010, 4911910090, 4911990000]),
            goods_nomenclature_sid=(x for x in [4911910010, 4911910090, 4911990000]),
            description=(x for x in ["Paper", "Scissors", "Rock"]),
            nomenclature_tree=self.tree,
        )
        self.client = Client()

    @classmethod
    def setUpClass(cls):
        super(CommoditySetupTestCase, cls).setUpClass()
        for index in indices:
            if not index.exists():
                index.save()


class CommoditySearchViewTestCase(CommoditySetupTestCase):
    """
    Test Commodity code Search view
    """

    def setUp(self):
        super().setUp()
        self.url = reverse("search:search-commodity-old", kwargs={"country_code": "au"})
        self.grouped_url = reverse(
            "search:search-commodity", kwargs={"country_code": "au"}
        )

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
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "search/commodity_search.html")

    def test_grouped_commodity_search_is_using_the_correct_template(self):
        response = self.client.get(self.grouped_url)
        self.assertTemplateUsed(response, "search/grouped_commodity_search.html")

    def test_search_view_returns_http_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_search_view_tracks_event(self):
        with mock.patch("search.views.track_event") as mock_track_event, mock.patch(
            "search.views.helpers.search_by_term"
        ) as mock_search_by_term, mock.patch(
            "search.views.helpers.get_alias_from_hit"
        ) as mock_get_alias_from_hit:

            mock_get_alias_from_hit.return_value = "chapter"
            mock_hit = mock.MagicMock()
            mock_hit.meta = {"index": "commodity", "score": 1}
            mock_hit.__getitem__.return_value = lambda x: "1234"
            hits = [mock_hit for _ in range(10)]
            mock_search_by_term.return_value = {
                "results": hits,
                "_all_results": hits,
                "page_range_start": 1,
                "page_range_end": 1,
                "total_pages": 1,
                "total_results": 10,
                "no_results": False,
            }

            response = self.client.get(
                self.url,
                data={
                    "q": "socks",
                    "toggle_headings": 0,
                    "sort": "ranking",
                    "sort_order": "desc",
                    "country": "jp",
                    "page": 0,
                },
            )

            mock_track_event.assert_called_once_with(
                response.wsgi_request,
                "search",
                "products results (au)",
                label="socks",
                value=10,
            )


class CommodityTermSearchAPIViewTestCase(CommoditySetupTestCase):
    """
    Test Commodity name search Search view
    """

    def test_search_view_missing_term_returns_http_400(self):
        resp = self.client.get(reverse("search:commodity-term-api-search"))
        self.assertEqual(resp.status_code, 400)

    def test_search_view_with_code__the_form_is_valid_follow_is_ok(self):
        url = reverse("search:commodity-term-api-search")
        resp = self.client.get(url, data={"q": "Scissors"})
        self.assertEqual(resp.status_code, 200)


class CommodityCodeSearchAPIViewTestCase(CommoditySetupTestCase):
    """
    Test Commodity code search Search view
    """

    def test_search_view_missing_term_returns_http_400(self):
        resp = self.client.get(reverse("search:commodity-code-api-search"))
        self.assertEqual(resp.status_code, 400)


class SearchFormTestCase(TestCase):
    def test_form_is_valid_with_a_query(self):
        form_data = {
            "q": "Paper",
            "country": "AU",
            "page": "1",
            "toggle_headings": 0,
            "sort_order": "asc",
            "sort": "ranking",
        }
        form = CommoditySearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_is_not_valid_with_missing_query(self):
        form_data = {"q": "", "country": "AU"}
        form = CommoditySearchForm(data=form_data)
        self.assertFalse(form.is_valid())


class CommodityKeywordSearchViewTestCase(TestCase):
    #     """
    #     Test Keyword Search view
    #     """

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpClass(cls):
        super(CommodityKeywordSearchViewTestCase, cls).setUpClass()
        for index in indices:
            if not index.exists():
                index.save()

    def test_commodity_keyword_search_query_is_empty(self):
        session = self.client.session
        session["origin_country"] = "AU"
        session.save()

        resp = self.client.get(
            reverse("search:search-commodity", kwargs={"country_code": "au"}),
            data={"q": "", "country": "au"},
        )

        self.assertEqual(resp.context["form"].is_valid(), False)

    def test_commodity_keyword_empty_search(self):
        session = self.client.session
        session["origin_country"] = "AU"
        session.save()

        resp = self.client.get(
            reverse("search:search-commodity", kwargs={"country_code": "au"}),
            data={
                "q": "nonexistent_product",
                "country": "au",
                "toggle_headings": 0,
                "sort": "ranking",
                "sort_order": "asc",
                "page": 1,
            },
        )

        self.assertEqual(resp.context["form"].is_valid(), False)
        self.assertEqual(resp.context["title_suffix"], " (no results)")


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

    def test_commodity_code_html(self):
        code = _commodity_code_html("4104115900")
        self.assertEqual(
            code,
            '<span class="app-commodity-code app-hierarchy-tree__commodity-code" aria-label="Commodity code"><span '
            'class="app-commodity-code__highlight app-commodity-code__highlight--1">41</span><span class="app-commodity-code__highlight app-commodity-code__highlight--2">04</span><span class="app-commodity-code__highlight app-commodity-code__highlight--3">11</span><span class="app-commodity-code__highlight app-commodity-code__highlight--4">59</span><span class="app-commodity-code__highlight app-commodity-code__highlight--5"><span class="app-commodity-code__is-blank">00</span></span></span>',
        )


class TestSearchHierarchyTestCase(TestCase):
    """
    Test search hierarchy view
    """

    def setUp(self):
        self.client = Client()

    def test_search_hierarchy(self):
        request = RequestFactory().get(
            reverse(
                "search:search-hierarchy",
                kwargs={"country_code": "au", "node_id": "section-1"},
            )
        )
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session["origin_country"] = "au"
        request.session.save()

        resp = search_hierarchy(request=request, node_id="section-1", country_code="au")
        self.assertEqual(resp.status_code, 200)

    def test_search_hierarchy_when_country_code_is_None(self):
        request = RequestFactory().get(
            reverse(
                "search:search-hierarchy",
                kwargs={"country_code": "au", "node_id": "section-1"},
            )
        )
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session["origin_country"] = None
        request.session.save()

        resp = search_hierarchy(request=request, node_id="section-1", country_code=None)
        self.assertEqual(resp.status_code, 302)


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


class TestHierarchyData(TestCase):
    def setUp(self):
        """
        To test fully test a commodity we need to load a parent subheading and its parent heading and save the
        relationships between the three model instances
        :return:
        """
        self.tree = create_nomenclature_tree(region="UK")

        self.section = create_instance(
            get_data(settings.SECTION_STRUCTURE, self.tree), Section
        )

        self.chapter = create_instance(
            get_data(settings.CHAPTER_STRUCTURE, self.tree), Chapter
        )
        self.chapter.section_id = self.section.pk
        self.chapter.save()

        self.heading = create_instance(
            get_data(settings.HEADING_STRUCTURE, self.tree), Heading
        )
        self.heading.chapter_id = self.chapter.pk
        self.heading.save()

        self.subheading = create_instance(
            get_data(settings.SUBHEADING_STRUCTURE, self.tree), SubHeading
        )
        self.subheading.heading_id = self.heading.id
        self.subheading.save()

        self.commodity = create_instance(
            get_data(settings.COMMODITY_STRUCTURE, self.tree), Commodity
        )
        self.commodity.parent_subheading_id = self.subheading.id
        self.commodity.tts_json = json.dumps(
            get_data(settings.COMMODITY_DATA, self.tree)
        )

        self.commodity.save()

        self.client = Client()

    def test_hierarchy_data_is_valid(self):
        response = self.client.get("/search/country/au/hierarchy/root")
        self.assertEqual(response.status_code, 200)

    def test_hierarchy_data_at_root(self):
        response = self.client.get("/search/country/au/hierarchy/root")
        self.assertInHTML(
            "Live animals; animal products", response.context["hierarchy_html"]
        )
        self.assertEqual(
            response.context["country_code"], settings.TEST_COUNTRY_CODE.lower()
        )

    def test_hierarchy_data_at_section(self):
        response = self.client.get("/search/country/au/hierarchy/section-2#section-2")
        self.assertInHTML(
            settings.TEST_SECTION_DESCRIPTION, response.context["hierarchy_html"]
        )
        self.assertEqual(
            response.context["country_code"], settings.TEST_COUNTRY_CODE.lower()
        )

    def test_hierarchy_data_at_chapter(self):
        chapter_id = Chapter.objects.get(
            chapter_code=settings.TEST_CHAPTER_CODE
        ).goods_nomenclature_sid
        response = self.client.get(
            "/search/country/au/hierarchy/chapter-{0}#chapter-{0}".format(chapter_id)
        )
        logger.debug(response.context["hierarchy_html"])
        self.assertInHTML(
            settings.TEST_SECTION_DESCRIPTION, response.context["hierarchy_html"]
        )
        self.assertInHTML(
            settings.TEST_CHAPTER_DESCRIPTION, response.context["hierarchy_html"]
        )
        self.assertEqual(
            response.context["country_code"], settings.TEST_COUNTRY_CODE.lower()
        )

    def test_hierarchy_data_at_heading(self):
        heading_id = Heading.objects.get(
            heading_code=settings.TEST_HEADING_CODE
        ).goods_nomenclature_sid
        response = self.client.get(
            "/search/country/au/hierarchy/heading-{0}#heading-{0}".format(heading_id)
        )
        self.assertInHTML(
            settings.TEST_SECTION_DESCRIPTION, response.context["hierarchy_html"]
        )
        self.assertInHTML(
            settings.TEST_CHAPTER_DESCRIPTION, response.context["hierarchy_html"]
        )
        self.assertInHTML(
            settings.TEST_HEADING_DESCRIPTION, response.context["hierarchy_html"]
        )
        self.assertEqual(
            response.context["country_code"], settings.TEST_COUNTRY_CODE.lower()
        )

    def test_hierarchy_data_at_subheading(self):
        subheading_id = SubHeading.objects.get(
            commodity_code="0101210000"
        ).goods_nomenclature_sid
        response = self.client.get(
            "/search/country/au/hierarchy/sub_heading-{0}#sub_heading-{0}".format(
                subheading_id
            )
        )
        self.assertInHTML(
            settings.TEST_SECTION_DESCRIPTION, response.context["hierarchy_html"]
        )
        self.assertInHTML(
            settings.TEST_CHAPTER_DESCRIPTION, response.context["hierarchy_html"]
        )
        self.assertInHTML(
            settings.TEST_HEADING_DESCRIPTION, response.context["hierarchy_html"]
        )
        self.assertInHTML(
            settings.TEST_SUBHEADING_DESCRIPTION, response.context["hierarchy_html"]
        )
        self.assertEqual(
            response.context["country_code"], settings.TEST_COUNTRY_CODE.lower()
        )


class TestSearchHierarchyAPITestCase(CommoditySetupTestCase):
    """
    Test search hierarchy view
    """

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_search_hierarchy(self):
        url = reverse("search:hierarchy-api-search")

        response = self.client.get(url, {"country_code": "au", "node_id": "section-1"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "results": [
                    {
                        "key": "section-10",
                        "type": "branch",
                        "roman_numeral": "X",
                        "chapter_range_str": "47 to 49",
                        "label": "Live animals; animal products",
                    }
                ]
            },
        )

    def test_search_hierarchy_when_country_code_is_None(self):
        response = self.client.get(
            reverse("search:hierarchy-api-search"), {"node_id": "section-1"}
        )

        self.assertEqual(response.status_code, 400)

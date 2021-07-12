import logging

from mixer.backend.django import mixer

from django.urls import reverse
from django.test import RequestFactory

from commodities.models import Commodity
from core.helpers import reset_urls_for_settings
from countries.models import Country
from hierarchy.helpers import create_nomenclature_tree
from hierarchy.models import Section, Chapter, Heading, SubHeading
from regulations.models import RegulationGroup

from ..forms import (
    ChapterAddForm,
    ChapterAddSearchForm,
    CommodityAddForm,
    CommodityAddSearchForm,
    HeadingAddForm,
    HeadingAddSearchForm,
    SubHeadingAddForm,
    SubHeadingAddSearchForm,
)

from .base import CMSTestCase

from ..views import (
    BaseRegulationGroupDetailView,
    RegulationGroupChapterAddView,
    RegulationGroupHeadingAddView,
    RegulationGroupSubHeadingAddView,
    RegulationGroupCommodityAddView,
)

logger = logging.getLogger(__name__)


def set_up_nomenclature(self):
    self.country = Country.objects.all().first()

    self.tree = create_nomenclature_tree("UK")

    self.section = mixer.blend(
        Section,
        nomenclature_tree=self.tree,
    )

    self.chapter = mixer.blend(
        Chapter,
        nomenclature_tree=self.tree,
        section=self.section,
        chapter_code="0100000000",
        goods_nomenclature_sid="264127",
    )

    self.heading = mixer.blend(
        Heading,
        nomenclature_tree=self.tree,
        chapter=self.chapter,
        heading_code="0101000000",
        goods_nomenclature_sid="2",
    )

    self.subheading = mixer.blend(
        SubHeading,
        nomenclature_tree=self.tree,
        heading=self.heading,
        commodity_code="010101000",
        goods_nomenclature_sid="2",
    )

    self.commodity = mixer.blend(
        Commodity,
        nomenclature_tree=self.tree,
        parent_subheading=self.subheading,
        commodity_code="010101011",
        goods_nomenclature_sid="2",
        description="Self Sealing Stem-Bolts",
    )

    self.reg_group = mixer.blend(
        RegulationGroup,
        nomenclature_trees=[self.tree],
        chapters=[self.chapter],
        headings=[self.heading],
    )


class TestRegulationGroupsList(CMSTestCase):
    def setUp(self):
        self.login()

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_initial_redirect(self):
        response = self.client.get(reverse("cms:home"))
        self.assertRedirects(response, "/cms/regulation-groups/")

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_list(self):
        mixer.cycle(20).blend(RegulationGroup)

        response = self.client.get(reverse("cms:regulation-groups-list"))
        self.assertTemplateUsed(response, "cms/regulations/regulationgroup_list.html")

        object_list = response.context["object_list"]
        self.assertEqual(object_list.count(), 10)

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_search(self):
        foo_regulation = mixer.blend(RegulationGroup, title="This is foo regulation")
        bar_regulation = mixer.blend(RegulationGroup, title="This is bar regulation")

        response = self.client.get(reverse("cms:regulation-groups-list"))
        object_list = response.context["object_list"]
        self.assertIn(foo_regulation, object_list)
        self.assertIn(bar_regulation, object_list)
        searching = response.context["searching"]
        self.assertFalse(searching)
        search_query = response.context["search_query"]
        self.assertEqual(search_query, None)

        response = self.client.get(reverse("cms:regulation-groups-list"), {"q": "foo"})
        object_list = response.context["object_list"]
        self.assertIn(foo_regulation, object_list)
        self.assertNotIn(bar_regulation, object_list)
        searching = response.context["searching"]
        self.assertTrue(searching)
        search_query = response.context["search_query"]
        self.assertEqual(search_query, "foo")

        response = self.client.get(reverse("cms:regulation-groups-list"), {"q": "bar"})
        object_list = response.context["object_list"]
        self.assertNotIn(foo_regulation, object_list)
        self.assertIn(bar_regulation, object_list)
        searching = response.context["searching"]
        self.assertTrue(searching)
        search_query = response.context["search_query"]
        self.assertEqual(search_query, "bar")

        response = self.client.get(
            reverse("cms:regulation-groups-list"), {"q": "regulation"}
        )
        object_list = response.context["object_list"]
        self.assertIn(foo_regulation, object_list)
        self.assertIn(bar_regulation, object_list)
        searching = response.context["searching"]
        self.assertTrue(searching)
        search_query = response.context["search_query"]
        self.assertEqual(search_query, "regulation")

        response = self.client.get(
            reverse("cms:regulation-groups-list"), {"q": "madeup"}
        )
        object_list = response.context["object_list"]
        self.assertNotIn(foo_regulation, object_list)
        self.assertNotIn(bar_regulation, object_list)
        searching = response.context["searching"]
        self.assertTrue(searching)
        search_query = response.context["search_query"]
        self.assertEqual(search_query, "madeup")


class TestRegulationGroupsCreate(CMSTestCase):
    def setUp(self):
        self.login()

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_group_create_view_form_template_loaded(self):
        response = self.client.get(reverse("cms:regulation-group-create"))
        self.assertTemplateUsed(response, "cms/regulations/regulationgroup_create.html")
        self.assertEqual(response.status_code, 200)

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_group_create_view_form_data_valid(self):
        response = self.client.post(
            reverse("cms:regulation-group-create"),
            data={
                "title": "Test_Form_Input",
            },
        )
        self.assertRedirects(response, "/cms/approval/2/")


class TestRegulationGroupDetailView(CMSTestCase):
    def setUp(self):
        self.login()
        self.request_factory = RequestFactory()
        set_up_nomenclature(self)

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_detail_panel_base(self):
        request = self.request_factory.get(
            reverse("cms:regulation-group-detail", kwargs={"pk": "1"})
        )
        detail_view = BaseRegulationGroupDetailView()
        detail_view.setup(request)
        detail_view.object = "placeholder_obj"
        detail_view.selected_panel = "a_panel"
        response = detail_view.get_context_data()
        self.assertEquals("a_panel", response["selected_panel"])

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_detail_panel_base_error_no_panel_selected(self):
        request = self.request_factory.get(
            reverse("cms:regulation-group-detail", kwargs={"pk": "1"})
        )
        detail_view = BaseRegulationGroupDetailView()
        detail_view.setup(request)
        detail_view.object = "placeholder_obj"
        self.assertRaises(NotImplementedError, lambda: detail_view.get_context_data())

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_detail_panel_views(self):
        reg_group = mixer.blend(
            RegulationGroup,
            nomenclature_trees=[self.tree],
            chapters=[self.chapter],
            headings=[self.heading],
        )

        url = reverse("cms:regulation-group-chapter-list", kwargs={"pk": reg_group.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "cms/regulations/regulationgroup_chapter_list.html"
        )

        url = reverse("cms:regulation-group-heading-list", kwargs={"pk": reg_group.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "cms/regulations/regulationgroup_heading_list.html"
        )

        url = reverse(
            "cms:regulation-group-subheading-list", kwargs={"pk": reg_group.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "cms/regulations/regulationgroup_subheading_list.html"
        )

        url = reverse(
            "cms:regulation-group-commodity-list", kwargs={"pk": reg_group.pk}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "cms/regulations/regulationgroup_commodities_list.html"
        )


class TestRegulationGroupAddViews(CMSTestCase):
    def setUp(self):
        self.login()
        self.request_factory = RequestFactory()
        set_up_nomenclature(self)

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_chapter_add_view(self):
        request = self.request_factory.get(
            reverse(
                "cms:regulation-group-chapter-add", kwargs={"pk": self.reg_group.pk}
            ),
        )

        detail_view = RegulationGroupChapterAddView()
        detail_view.setup(request, pk=self.reg_group.pk)
        detail_view.object = self.reg_group

        context = detail_view.get_context_data()
        self.assertIsInstance(context["add_form"], ChapterAddForm)
        self.assertIsInstance(context["search_form"], ChapterAddSearchForm)

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_chapter_add_form_submitted(self):
        response = self.client.post(
            reverse(
                "cms:regulation-group-chapter-add", kwargs={"pk": self.reg_group.pk}
            ),
            data={"chapters": self.chapter.goods_nomenclature_sid},
        )
        url_str = "/cms/approval/" + str(self.reg_group.pk) + "/"
        self.assertRedirects(response, url_str)

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_chapter_remove_form_submitted(self):
        response = self.client.post(
            reverse(
                "cms:regulation-group-chapter-remove",
                kwargs={"pk": self.reg_group.pk, "chapter_pk": self.chapter.pk},
            ),
        )
        remove_content_html = (
            "Remove <em>"
            + self.chapter.description
            + "</em> from <em>"
            + self.reg_group.title
            + "</em>?"
        )
        self.assertContains(
            response,
            remove_content_html,
            status_code=200,
            html=True,
        )

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_heading_add_view(self):
        request = self.request_factory.get(
            reverse(
                "cms:regulation-group-heading-add", kwargs={"pk": self.reg_group.pk}
            ),
        )

        detail_view = RegulationGroupHeadingAddView()
        detail_view.setup(request, pk=self.reg_group.pk)
        detail_view.object = self.reg_group

        context = detail_view.get_context_data()
        self.assertIsInstance(context["add_form"], HeadingAddForm)
        self.assertIsInstance(context["search_form"], HeadingAddSearchForm)

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_subheading_add_view(self):
        request = self.request_factory.get(
            reverse(
                "cms:regulation-group-subheading-add", kwargs={"pk": self.reg_group.pk}
            ),
        )

        detail_view = RegulationGroupSubHeadingAddView()
        detail_view.setup(request, pk=self.reg_group.pk)
        detail_view.object = self.reg_group

        context = detail_view.get_context_data()
        self.assertIsInstance(context["add_form"], SubHeadingAddForm)
        self.assertIsInstance(context["search_form"], SubHeadingAddSearchForm)

    @reset_urls_for_settings(CMS_ENABLED=True)
    def test_commodity_add_view(self):
        request = self.request_factory.get(
            reverse(
                "cms:regulation-group-commodity-add", kwargs={"pk": self.reg_group.pk}
            ),
        )

        detail_view = RegulationGroupCommodityAddView()
        detail_view.setup(request, pk=self.reg_group.pk)
        detail_view.object = self.reg_group

        context = detail_view.get_context_data()
        self.assertIsInstance(context["add_form"], CommodityAddForm)
        self.assertIsInstance(context["search_form"], CommodityAddSearchForm)

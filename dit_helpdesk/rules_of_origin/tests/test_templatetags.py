from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse

from mixer.backend.django import mixer
from parameterized import parameterized

from commodities.models import Commodity
from countries.models import Country
from hierarchy.helpers import create_nomenclature_tree
from hierarchy.models import Chapter, Heading, SubHeading


class LinkifyHsCodesTestCase(TestCase):
    def render_linkify_hs_codes(self, value, country_code):
        template_string = f'{{% load rules_of_origin %}}{{{{value|linkify_hs_codes:"{country_code}"}}}}'
        template = Template(template_string)

        return template.render(Context({"value": value}))

    def get_link_element(self, text, detail_url, hierarchy_url):
        return (
            f'<a class="govuk-link hierarchy-modal" data-toggle="modal" data-target="hierarchy-modal" '
            f'data-href="{hierarchy_url}" href="{detail_url}">{text}</a>'
        )

    def get_object_urls(self, model_type, object, country):
        detail_url = reverse(
            f"{model_type}-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": object.commodity_code,
                "nomenclature_sid": object.goods_nomenclature_sid,
            },
        )
        hierarchy_url = reverse(
            "hierarchy-context-tree",
            kwargs={
                "commodity_type": model_type,
                "commodity_code": object.commodity_code,
                "nomenclature_sid": object.goods_nomenclature_sid,
                "country_code": country.country_code.lower(),
            },
        )

        return detail_url, hierarchy_url

    def test_linkify_no_matching_models(self):
        country = mixer.blend(Country, country_code="XX")

        result = self.render_linkify_hs_codes(
            "Chapter 1",
            country.country_code,
        )
        self.assertEqual(result, "Chapter 1")

        result = self.render_linkify_hs_codes(
            "Heading 0101",
            country.country_code,
        )
        self.assertEqual(result, "Heading 0101")

        result = self.render_linkify_hs_codes(
            "Subheading 0101",
            country.country_code,
        )
        self.assertEqual(result, "Subheading 0101")

        result = self.render_linkify_hs_codes(
            "Subheading 0101.01",
            country.country_code,
        )
        self.assertEqual(result, "Subheading 0101.01")

    def test_linkify_chapter_hs_codes(self):
        tree = create_nomenclature_tree("UK")
        country = mixer.blend(Country, country_code="XX")
        chapter_01 = mixer.blend(
            Chapter,
            chapter_code="0100000000",
            goods_nomenclature_sid="01",
            nomenclature_tree=tree,
        )
        chapter_10 = mixer.blend(
            Chapter,
            chapter_code="1000000000",
            goods_nomenclature_sid="10",
            nomenclature_tree=tree,
        )

        chapter_01_detail_url, chapter_01_hierarchy_url = self.get_object_urls(
            "chapter", chapter_01, country
        )
        chapter_01_link_element = self.get_link_element(
            "1", chapter_01_detail_url, chapter_01_hierarchy_url
        )
        result = self.render_linkify_hs_codes(
            "Chapter 1 more text",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"Chapter {chapter_01_link_element} more text",
        )
        result = self.render_linkify_hs_codes(
            "chapter 1 more text",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"chapter {chapter_01_link_element} more text",
        )

        chapter_10_detail_url, chapter_10_hierarchy_url = self.get_object_urls(
            "chapter", chapter_10, country
        )
        chapter_10_link_element = self.get_link_element(
            "10", chapter_10_detail_url, chapter_10_hierarchy_url
        )
        result = self.render_linkify_hs_codes(
            "Chapter 10",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"Chapter {chapter_10_link_element}",
        )
        result = self.render_linkify_hs_codes(
            "chapter 10",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"chapter {chapter_10_link_element}",
        )

    def test_linkify_multiple_chapters_hs_codes(self):
        tree = create_nomenclature_tree("UK")
        country = mixer.blend(Country, country_code="XX")
        chapter_10 = mixer.blend(
            Chapter,
            chapter_code="1000000000",
            goods_nomenclature_sid="10",
            nomenclature_tree=tree,
        )
        chapter_20 = mixer.blend(
            Chapter,
            chapter_code="2000000000",
            goods_nomenclature_sid="20",
            nomenclature_tree=tree,
        )
        chapter_30 = mixer.blend(
            Chapter,
            chapter_code="3000000000",
            goods_nomenclature_sid="30",
            nomenclature_tree=tree,
        )

        chapter_10_detail_url, chapter_10_hierarchy_url = self.get_object_urls(
            "chapter", chapter_10, country
        )
        chapter_10_link_element = self.get_link_element(
            "10", chapter_10_detail_url, chapter_10_hierarchy_url
        )
        chapter_20_detail_url, chapter_20_hierarchy_url = self.get_object_urls(
            "chapter", chapter_20, country
        )
        chapter_20_link_element = self.get_link_element(
            "20", chapter_20_detail_url, chapter_20_hierarchy_url
        )
        chapter_30_detail_url, chapter_30_hierarchy_url = self.get_object_urls(
            "chapter", chapter_30, country
        )
        chapter_30_link_element = self.get_link_element(
            "30", chapter_30_detail_url, chapter_30_hierarchy_url
        )

        result = self.render_linkify_hs_codes(
            "Chapters 10 and 20",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"Chapters {chapter_10_link_element} and {chapter_20_link_element}",
        )

        result = self.render_linkify_hs_codes(
            "chapters 10 and 20",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"chapters {chapter_10_link_element} and {chapter_20_link_element}",
        )

        result = self.render_linkify_hs_codes(
            "Chapters 10, 20 and 30",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"Chapters {chapter_10_link_element}, {chapter_20_link_element} and {chapter_30_link_element}",
        )

        result = self.render_linkify_hs_codes(
            "chapters 10, 20 and 30",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"chapters {chapter_10_link_element}, {chapter_20_link_element} and {chapter_30_link_element}",
        )

    def test_linkify_heading_hs_codes(self):
        tree = create_nomenclature_tree("UK")
        country = mixer.blend(Country, country_code="XX")
        heading = mixer.blend(
            Heading,
            heading_code="0101000000",
            goods_nomenclature_sid="0101",
            nomenclature_tree=tree,
        )

        heading_detail_url, heading_hierarchy_url = self.get_object_urls(
            "heading", heading, country
        )

        heading_link_element = self.get_link_element(
            "0101", heading_detail_url, heading_hierarchy_url
        )
        result = self.render_linkify_hs_codes(
            "Heading 0101",
            country.country_code,
        )
        self.assertEqual(result, f"Heading {heading_link_element}")

        result = self.render_linkify_hs_codes(
            "heading 0101",
            country.country_code,
        )
        self.assertEqual(result, f"heading {heading_link_element}")

        heading_link_element = self.get_link_element(
            "01.01", heading_detail_url, heading_hierarchy_url
        )
        result = self.render_linkify_hs_codes(
            "Heading 01.01",
            country.country_code,
        )
        self.assertEqual(result, f"Heading {heading_link_element}")

        result = self.render_linkify_hs_codes(
            "heading 01.01",
            country.country_code,
        )
        self.assertEqual(result, f"heading {heading_link_element}")

    def test_linkify_multiple_headings_hs_codes(self):
        tree = create_nomenclature_tree("UK")
        country = mixer.blend(Country, country_code="XX")
        heading_0101 = mixer.blend(
            Heading,
            heading_code="0101000000",
            goods_nomenclature_sid="0101",
            nomenclature_tree=tree,
        )
        heading_0202 = mixer.blend(
            Heading,
            heading_code="0202000000",
            goods_nomenclature_sid="0202",
            nomenclature_tree=tree,
        )
        heading_0303 = mixer.blend(
            Heading,
            heading_code="0303000000",
            goods_nomenclature_sid="0303",
            nomenclature_tree=tree,
        )

        heading_0101_detail_url, heading_0101_hierarchy_url = self.get_object_urls(
            "heading", heading_0101, country
        )
        heading_0101_link_element = self.get_link_element(
            "0101", heading_0101_detail_url, heading_0101_hierarchy_url
        )
        heading_0202_detail_url, heading_0202_hierarchy_url = self.get_object_urls(
            "heading", heading_0202, country
        )
        heading_0202_link_element = self.get_link_element(
            "0202", heading_0202_detail_url, heading_0202_hierarchy_url
        )
        heading_0303_detail_url, heading_0303_hierarchy_url = self.get_object_urls(
            "heading", heading_0303, country
        )
        heading_0303_link_element = self.get_link_element(
            "0303", heading_0303_detail_url, heading_0303_hierarchy_url
        )

        result = self.render_linkify_hs_codes(
            "Headings 0101 and 0202",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"Headings {heading_0101_link_element} and {heading_0202_link_element}",
        )

        result = self.render_linkify_hs_codes(
            "headings 0101 and 0202",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"headings {heading_0101_link_element} and {heading_0202_link_element}",
        )

        result = self.render_linkify_hs_codes(
            "Headings 0101, 0202 and 0303",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"Headings {heading_0101_link_element}, {heading_0202_link_element} and {heading_0303_link_element}",
        )

        result = self.render_linkify_hs_codes(
            "headings 0101, 0202 and 0303",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"headings {heading_0101_link_element}, {heading_0202_link_element} and {heading_0303_link_element}",
        )

    def test_linkify_subheading_hs_codes(self):
        tree = create_nomenclature_tree("UK")
        country = mixer.blend(Country, country_code="XX")
        subheading_0101 = mixer.blend(
            SubHeading,
            commodity_code="0101000000",
            goods_nomenclature_sid="0101",
            nomenclature_tree=tree,
        )
        subheading_010101 = mixer.blend(
            SubHeading,
            commodity_code="0101010000",
            goods_nomenclature_sid="010101",
            nomenclature_tree=tree,
        )

        (
            subheading_0101_detail_url,
            subheading_0101_hierarchy_url,
        ) = self.get_object_urls(
            "subheading",
            subheading_0101,
            country,
        )
        (
            subheading_010101_detail_url,
            subheading_010101_hierarchy_url,
        ) = self.get_object_urls(
            "subheading",
            subheading_010101,
            country,
        )

        subheading_0101_link_element = self.get_link_element(
            "0101",
            subheading_0101_detail_url,
            subheading_0101_hierarchy_url,
        )
        result = self.render_linkify_hs_codes(
            "Subheading 0101",
            country.country_code,
        )
        self.assertEqual(result, f"Subheading {subheading_0101_link_element}")

        result = self.render_linkify_hs_codes(
            "subheading 0101",
            country.country_code,
        )
        self.assertEqual(result, f"subheading {subheading_0101_link_element}")

        subheading_0101_link_element = self.get_link_element(
            "01.01",
            subheading_0101_detail_url,
            subheading_0101_hierarchy_url,
        )
        result = self.render_linkify_hs_codes(
            "Subheading 01.01",
            country.country_code,
        )
        self.assertEqual(result, f"Subheading {subheading_0101_link_element}")

        result = self.render_linkify_hs_codes(
            "subheading 01.01",
            country.country_code,
        )
        self.assertEqual(result, f"subheading {subheading_0101_link_element}")

        subheading_010101_link_element = self.get_link_element(
            "0101.01",
            subheading_010101_detail_url,
            subheading_010101_hierarchy_url,
        )
        result = self.render_linkify_hs_codes(
            "Subheading 0101.01",
            country.country_code,
        )
        self.assertEqual(result, f"Subheading {subheading_010101_link_element}")

        result = self.render_linkify_hs_codes(
            "subheading 0101.01",
            country.country_code,
        )
        self.assertEqual(result, f"subheading {subheading_010101_link_element}")

    def test_linkify_multiple_subheadings_hs_codes(self):
        tree = create_nomenclature_tree("UK")
        country = mixer.blend(Country, country_code="XX")
        subheading_0101 = mixer.blend(
            SubHeading,
            commodity_code="0101000000",
            goods_nomenclature_sid="0101",
            nomenclature_tree=tree,
        )
        subheading_0202 = mixer.blend(
            SubHeading,
            commodity_code="0202000000",
            goods_nomenclature_sid="0202",
            nomenclature_tree=tree,
        )
        subheading_010101 = mixer.blend(
            SubHeading,
            commodity_code="0101010000",
            goods_nomenclature_sid="010101",
            nomenclature_tree=tree,
        )

        (
            subheading_0101_detail_url,
            subheading_0101_hierarchy_url,
        ) = self.get_object_urls(
            "subheading",
            subheading_0101,
            country,
        )
        subheading_0101_link_element = self.get_link_element(
            "0101",
            subheading_0101_detail_url,
            subheading_0101_hierarchy_url,
        )

        (
            subheading_0202_detail_url,
            subheading_0202_hierarchy_url,
        ) = self.get_object_urls(
            "subheading",
            subheading_0202,
            country,
        )
        subheading_0202_link_element = self.get_link_element(
            "02.02",
            subheading_0202_detail_url,
            subheading_0202_hierarchy_url,
        )

        (
            subheading_010101_detail_url,
            subheading_010101_hierarchy_url,
        ) = self.get_object_urls(
            "subheading",
            subheading_010101,
            country,
        )
        subheading_010101_link_element = self.get_link_element(
            "0101.01",
            subheading_010101_detail_url,
            subheading_010101_hierarchy_url,
        )

        result = self.render_linkify_hs_codes(
            "Subheadings 0101 and 02.02",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"Subheadings {subheading_0101_link_element} and {subheading_0202_link_element}",
        )

        result = self.render_linkify_hs_codes(
            "subheadings 0101 and 02.02",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"subheadings {subheading_0101_link_element} and {subheading_0202_link_element}",
        )

        result = self.render_linkify_hs_codes(
            "Subheadings 0101, 02.02 and 0101.01",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"Subheadings {subheading_0101_link_element}, {subheading_0202_link_element} "
            f"and {subheading_010101_link_element}",
        )

        result = self.render_linkify_hs_codes(
            "subheadings 0101, 02.02 and 0101.01",
            country.country_code,
        )
        self.assertEqual(
            result,
            f"subheadings {subheading_0101_link_element}, {subheading_0202_link_element} "
            f"and {subheading_010101_link_element}",
        )

    def test_linkify_commodity_hs_codes(self):
        tree = create_nomenclature_tree("UK")
        country = mixer.blend(Country, country_code="XX")
        commodity_010101 = mixer.blend(
            Commodity,
            commodity_code="0101010000",
            goods_nomenclature_sid="010101",
            nomenclature_tree=tree,
        )

        (
            commodity_010101_detail_url,
            commodity_010101_hierarchy_url,
        ) = self.get_object_urls(
            "commodity",
            commodity_010101,
            country,
        )
        commodity_010101_link_element = self.get_link_element(
            "0101.01",
            commodity_010101_detail_url,
            commodity_010101_hierarchy_url,
        )

        result = self.render_linkify_hs_codes(
            "Subheading 0101.01",
            country.country_code,
        )
        self.assertEqual(result, f"Subheading {commodity_010101_link_element}")

        result = self.render_linkify_hs_codes(
            "subheading 0101.01",
            country.country_code,
        )
        self.assertEqual(result, f"subheading {commodity_010101_link_element}")

    def test_matches_spanning_multiple_models_matches_lowest(self):
        tree = create_nomenclature_tree("UK")
        country = mixer.blend(Country, country_code="XX")
        mixer.blend(
            Heading,
            heading_code="0101000000",
            goods_nomenclature_sid="0101",
            nomenclature_tree=tree,
        )
        subheading_0101 = mixer.blend(
            SubHeading,
            commodity_code="0101000000",
            goods_nomenclature_sid="0101",
            nomenclature_tree=tree,
        )
        mixer.blend(
            SubHeading,
            commodity_code="0101010000",
            goods_nomenclature_sid="010101",
            nomenclature_tree=tree,
        )
        commodity_010101 = mixer.blend(
            Commodity,
            commodity_code="0101010000",
            goods_nomenclature_sid="010101",
            nomenclature_tree=tree,
        )

        (
            subheading_0101_detail_url,
            subheading_0101_hierarchy_url,
        ) = self.get_object_urls(
            "subheading",
            subheading_0101,
            country,
        )
        subheading_0101_link_element = self.get_link_element(
            "0101",
            subheading_0101_detail_url,
            subheading_0101_hierarchy_url,
        )

        (
            commodity_010101_detail_url,
            commodity_010101_hierarchy_url,
        ) = self.get_object_urls(
            "commodity",
            commodity_010101,
            country,
        )
        commodity_010101_link_element = self.get_link_element(
            "0101.01",
            commodity_010101_detail_url,
            commodity_010101_hierarchy_url,
        )

        result = self.render_linkify_hs_codes(
            "Heading 0101",
            country.country_code,
        )
        self.assertEqual(result, f"Heading {subheading_0101_link_element}")

        result = self.render_linkify_hs_codes(
            "Subheading 0101.01",
            country.country_code,
        )
        self.assertEqual(result, f"Subheading {commodity_010101_link_element}")


class AnnotateAbbreviations(TestCase):
    def render_annotate_abbreviations(self, value):
        template_string = "{% load rules_of_origin %}{{value|annotate_abbreviations}}"
        template = Template(template_string)

        return template.render(Context({"value": value}))

    def test_no_abbreviations(self):
        result = self.render_annotate_abbreviations("no abbreviations")
        self.assertEqual(result, "no abbreviations")

    @parameterized.expand(
        [
            ("CC", "Change of Chapter"),
            ("CTH", "Change in tariff heading"),
            ("CTSH", "Change in tariff subheading"),
            ("MaxNOM", "Maximum value of non-originating materials"),
        ]
    )
    def test_replace_abbreviation(self, abbr, definition):
        result = self.render_annotate_abbreviations(
            f"The abbreviation {abbr} is an abbreviation"
        )
        self.assertEqual(
            result,
            f'The abbreviation <abbr title="{definition}">{abbr}</abbr> is an abbreviation',
        )

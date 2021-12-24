from django.test import TestCase
from django.urls import reverse

from mixer.backend.django import mixer

from commodities.models import Commodity
from countries.models import Country
from hierarchy.helpers import create_nomenclature_tree
from hierarchy.models import Chapter, Heading, SubHeading


from ..templatetags.rules_of_origin import linkify_hs_codes


class TemplateTagsTestCase(TestCase):
    def test_linkify_no_matching_models(self):
        country = mixer.blend(Country, country_code="XX")

        result = linkify_hs_codes(
            "Chapter 1",
            country.country_code,
        )
        self.assertEqual(result, "Chapter 1")

        result = linkify_hs_codes(
            "Heading 0101",
            country.country_code,
        )
        self.assertEqual(result, "Heading 0101")

        result = linkify_hs_codes(
            "Subheading 0101",
            country.country_code,
        )
        self.assertEqual(result, "Subheading 0101")

        result = linkify_hs_codes(
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

        chapter_01_url = reverse(
            "chapter-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": chapter_01.chapter_code,
                "nomenclature_sid": chapter_01.goods_nomenclature_sid,
            },
        )
        chapter_10_url = reverse(
            "chapter-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": chapter_10.chapter_code,
                "nomenclature_sid": chapter_10.goods_nomenclature_sid,
            },
        )

        result = linkify_hs_codes(
            "Chapter 1 more text",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Chapter <a class="govuk-link" href="{chapter_01_url}">1</a> more text',
        )

        result = linkify_hs_codes(
            "chapter 1 more text",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'chapter <a class="govuk-link" href="{chapter_01_url}">1</a> more text',
        )

        result = linkify_hs_codes(
            "Chapter 10",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Chapter <a class="govuk-link" href="{chapter_10_url}">10</a>',
        )

        result = linkify_hs_codes(
            "chapter 10",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'chapter <a class="govuk-link" href="{chapter_10_url}">10</a>',
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

        chapter_10_url = reverse(
            "chapter-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": chapter_10.chapter_code,
                "nomenclature_sid": chapter_10.goods_nomenclature_sid,
            },
        )
        chapter_20_url = reverse(
            "chapter-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": chapter_20.chapter_code,
                "nomenclature_sid": chapter_20.goods_nomenclature_sid,
            },
        )
        chapter_30_url = reverse(
            "chapter-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": chapter_30.chapter_code,
                "nomenclature_sid": chapter_30.goods_nomenclature_sid,
            },
        )

        result = linkify_hs_codes(
            "Chapters 10 and 20",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Chapters <a class="govuk-link" href="{chapter_10_url}">10</a> and '
            f'<a class="govuk-link" href="{chapter_20_url}">20</a>',
        )

        result = linkify_hs_codes(
            "chapters 10 and 20",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'chapters <a class="govuk-link" href="{chapter_10_url}">10</a> and '
            f'<a class="govuk-link" href="{chapter_20_url}">20</a>',
        )

        result = linkify_hs_codes(
            "Chapters 10, 20 and 30",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Chapters <a class="govuk-link" href="{chapter_10_url}">10</a>, '
            f'<a class="govuk-link" href="{chapter_20_url}">20</a> and '
            f'<a class="govuk-link" href="{chapter_30_url}">30</a>',
        )

        result = linkify_hs_codes(
            "chapters 10, 20 and 30",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'chapters <a class="govuk-link" href="{chapter_10_url}">10</a>, '
            f'<a class="govuk-link" href="{chapter_20_url}">20</a> and '
            f'<a class="govuk-link" href="{chapter_30_url}">30</a>',
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

        heading_url = reverse(
            "heading-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": heading.heading_code,
                "nomenclature_sid": heading.goods_nomenclature_sid,
            },
        )

        result = linkify_hs_codes(
            "Heading 0101",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Heading <a class="govuk-link" href="{heading_url}">0101</a>',
        )

        result = linkify_hs_codes(
            "Heading 01.01",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Heading <a class="govuk-link" href="{heading_url}">01.01</a>',
        )

        result = linkify_hs_codes(
            "heading 0101",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'heading <a class="govuk-link" href="{heading_url}">0101</a>',
        )

        result = linkify_hs_codes(
            "heading 01.01",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'heading <a class="govuk-link" href="{heading_url}">01.01</a>',
        )

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

        heading_0101_url = reverse(
            "heading-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": heading_0101.heading_code,
                "nomenclature_sid": heading_0101.goods_nomenclature_sid,
            },
        )
        heading_0202_url = reverse(
            "heading-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": heading_0202.heading_code,
                "nomenclature_sid": heading_0202.goods_nomenclature_sid,
            },
        )
        heading_0303_url = reverse(
            "heading-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": heading_0303.heading_code,
                "nomenclature_sid": heading_0303.goods_nomenclature_sid,
            },
        )

        result = linkify_hs_codes(
            "Headings 0101 and 0202",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Headings <a class="govuk-link" href="{heading_0101_url}">0101</a> and '
            f'<a class="govuk-link" href="{heading_0202_url}">0202</a>',
        )

        result = linkify_hs_codes(
            "headings 0101 and 0202",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'headings <a class="govuk-link" href="{heading_0101_url}">0101</a> and '
            f'<a class="govuk-link" href="{heading_0202_url}">0202</a>',
        )

        result = linkify_hs_codes(
            "Headings 0101, 0202 and 0303",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Headings <a class="govuk-link" href="{heading_0101_url}">0101</a>, '
            f'<a class="govuk-link" href="{heading_0202_url}">0202</a> and '
            f'<a class="govuk-link" href="{heading_0303_url}">0303</a>',
        )

        result = linkify_hs_codes(
            "headings 0101, 0202 and 0303",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'headings <a class="govuk-link" href="{heading_0101_url}">0101</a>, '
            f'<a class="govuk-link" href="{heading_0202_url}">0202</a> and '
            f'<a class="govuk-link" href="{heading_0303_url}">0303</a>',
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

        subheading_0101_url = reverse(
            "subheading-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": subheading_0101.commodity_code,
                "nomenclature_sid": subheading_0101.goods_nomenclature_sid,
            },
        )

        subheading_010101_url = reverse(
            "subheading-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": subheading_010101.commodity_code,
                "nomenclature_sid": subheading_010101.goods_nomenclature_sid,
            },
        )

        result = linkify_hs_codes(
            "Subheading 0101",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Subheading <a class="govuk-link" href="{subheading_0101_url}">0101</a>',
        )

        result = linkify_hs_codes(
            "Subheading 01.01",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Subheading <a class="govuk-link" href="{subheading_0101_url}">01.01</a>',
        )

        result = linkify_hs_codes(
            "subheading 0101",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'subheading <a class="govuk-link" href="{subheading_0101_url}">0101</a>',
        )

        result = linkify_hs_codes(
            "subheading 01.01",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'subheading <a class="govuk-link" href="{subheading_0101_url}">01.01</a>',
        )

        result = linkify_hs_codes(
            "Subheading 0101.01",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Subheading <a class="govuk-link" href="{subheading_010101_url}">0101.01</a>',
        )

        result = linkify_hs_codes(
            "subheading 0101.01",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'subheading <a class="govuk-link" href="{subheading_010101_url}">0101.01</a>',
        )

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

        subheading_0101_url = reverse(
            "subheading-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": subheading_0101.commodity_code,
                "nomenclature_sid": subheading_0101.goods_nomenclature_sid,
            },
        )
        subheading_0202_url = reverse(
            "subheading-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": subheading_0202.commodity_code,
                "nomenclature_sid": subheading_0202.goods_nomenclature_sid,
            },
        )
        subheading_010101_url = reverse(
            "subheading-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": subheading_010101.commodity_code,
                "nomenclature_sid": subheading_010101.goods_nomenclature_sid,
            },
        )

        result = linkify_hs_codes(
            "Subheadings 0101 and 02.02",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Subheadings <a class="govuk-link" href="{subheading_0101_url}">0101</a> and '
            f'<a class="govuk-link" href="{subheading_0202_url}">02.02</a>',
        )

        result = linkify_hs_codes(
            "subheadings 0101 and 02.02",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'subheadings <a class="govuk-link" href="{subheading_0101_url}">0101</a> and '
            f'<a class="govuk-link" href="{subheading_0202_url}">02.02</a>',
        )

        result = linkify_hs_codes(
            "Subheadings 0101, 02.02 and 0101.01",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Subheadings <a class="govuk-link" href="{subheading_0101_url}">0101</a>, '
            f'<a class="govuk-link" href="{subheading_0202_url}">02.02</a> and '
            f'<a class="govuk-link" href="{subheading_010101_url}">0101.01</a>',
        )

        result = linkify_hs_codes(
            "subheadings 0101, 02.02 and 0101.01",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'subheadings <a class="govuk-link" href="{subheading_0101_url}">0101</a>, '
            f'<a class="govuk-link" href="{subheading_0202_url}">02.02</a> and '
            f'<a class="govuk-link" href="{subheading_010101_url}">0101.01</a>',
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

        commodity_010101_url = reverse(
            "commodity-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": commodity_010101.commodity_code,
                "nomenclature_sid": commodity_010101.goods_nomenclature_sid,
            },
        )

        result = linkify_hs_codes(
            "Subheading 0101.01",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Subheading <a class="govuk-link" href="{commodity_010101_url}">0101.01</a>',
        )

        result = linkify_hs_codes(
            "subheading 0101.01",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'subheading <a class="govuk-link" href="{commodity_010101_url}">0101.01</a>',
        )

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

        subheading_0101_url = reverse(
            "subheading-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": subheading_0101.commodity_code,
                "nomenclature_sid": subheading_0101.goods_nomenclature_sid,
            },
        )
        commodity_010101_url = reverse(
            "commodity-detail",
            kwargs={
                "country_code": country.country_code.lower(),
                "commodity_code": commodity_010101.commodity_code,
                "nomenclature_sid": commodity_010101.goods_nomenclature_sid,
            },
        )

        result = linkify_hs_codes(
            "Heading 0101",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Heading <a class="govuk-link" href="{subheading_0101_url}">0101</a>',
        )

        result = linkify_hs_codes(
            "Subheading 0101.01",
            country.country_code,
        )
        self.assertEqual(
            result,
            f'Subheading <a class="govuk-link" href="{commodity_010101_url}">0101.01</a>',
        )

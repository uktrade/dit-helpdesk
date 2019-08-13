import logging
from django.test import TestCase
from django.urls import NoReverseMatch
from model_mommy.recipe import seq
from mixer.backend.django import mixer
from commodities.models import Commodity
from hierarchy.models import SubHeading, Heading, Section, Chapter, ROMAN_NUMERALS
# from trade_tariff_service.tts_api import HeadingJson

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class SectionTestCase(TestCase):

    """
    Test Section model
    """
    def setUp(self):

        self.section = mixer.blend(
            Section,
            section_id=1,
            roman_numeral=ROMAN_NUMERALS[1],
            tts_json="{}"
        )

    def test_str(self):
        self.assertEquals(str(self.section), "Section {0}".format(self.section.roman_numeral))

    def test_tts_json_is_a_string_representing_an_empty_json_object(self):
        # TODO: remove field from Section Model
        self.assertTrue(isinstance(self.section.tts_json, str))
        self.assertEquals(self.section.tts_json, "{}")

    def test_section_has_correct_roman_numeral(self):
        # TODO: remove field and create a property method
        logger.debug("{0}, {1}".format(ROMAN_NUMERALS[self.section.section_id], self.section.roman_numeral))
        self.assertEquals(ROMAN_NUMERALS[self.section.section_id], self.section.roman_numeral)

    def test_hierarchy_key(self):
        self.assertEquals(self.section.hierarchy_key, 'section-{0}'.format(self.section.pk))

    def test_has_hierarchy_children(self):
        self.chapters = mixer.cycle(5).blend(
            Chapter,
            section=self.section,
            chapter_code=seq(0)
        )
        self.assertTrue(len(self.section.get_hierarchy_children()) == 5)

    def test_chapters_url_raises_NoReverseMatchError(self):
        # TODO: remove method
        self.assertRaises(NoReverseMatch, lambda: self.section.get_chapters_url())

    def test_hierarchy_url(self):
        self.assertEquals(self.section.get_hierarchy_url(country_code="au"),
                          "/search/country/au/hierarchy/{0}".format(self.section.hierarchy_key))

    def test_hierarchy_url_without_country_code(self):
        self.assertRaises(NoReverseMatch, lambda: self.section.get_hierarchy_url())

    def test_hierarchy_url_with_uppercased_country_code(self):
        self.assertEquals(self.section.get_hierarchy_url(country_code="AU"),
                          "/search/country/au/hierarchy/{0}".format(self.section.hierarchy_key))

    def test_chapter_range_str_without_child_chapters_returns_None_as_str(self):
        self.assertEquals(self.section.chapter_range_str, 'None')

    def test_chapter_range_str_with_one_child_chapter_with_chapter_id_1(self):
        self.chapters = mixer.cycle(1).blend(
            Chapter,
            section=self.section,
            chapter_code=seq(0)
        )
        self.assertEquals(self.section.chapter_range_str, "1")

    def test_chapter_range_str_with_5_chapters_returns_1_to_5_as_str(self):
        self.chapters = mixer.cycle(5).blend(
            Chapter,
            section=self.section,
            chapter_code=seq(0)
        )
        self.assertEquals(self.section.chapter_range_str, "1 to 5")


class ChapterTestCase(TestCase):

    """
    Test Chapter Model
    """
    def setUp(self):

        self.chapter = mixer.blend(
            Chapter,
            tts_json="{}",
        )

    def test_str(self):
        self.assertEquals(str(self.chapter), "Chapter {0}".format(self.chapter.chapter_code))

    def test_title_is_equal_to_description(self):
        self.assertEquals(self.chapter.title, self.chapter.description)

    def test_hierarchy_key(self):
        self.assertEquals(self.chapter.hierarchy_key, 'chapter-{0}'.format(self.chapter.pk))

    def test_harmonized_code_equals_chapter_code(self):
        # TODO: Where is this property method used
        self.assertEquals(self.chapter.harmonized_code, self.chapter.chapter_code)

    def test_chapters_url_raises_NoReverseMatchError(self):
        # TODO: remove method
        self.assertRaises(NoReverseMatch, lambda: self.chapter.get_headings_url())

    def test_hierarchy_url(self):
        logger.debug(self.chapter.get_hierarchy_url(country_code="au"))
        self.assertEquals(self.chapter.get_hierarchy_url(country_code="au"),
                          "/search/country/au/hierarchy/{0}".format(self.chapter.hierarchy_key))

    def test_hierarchy_url_without_country_code(self):
        self.assertRaises(NoReverseMatch, lambda: self.chapter.get_hierarchy_url())

    def test_hierarchy_url_with_uppercased_country_code(self):
        self.assertEquals(self.chapter.get_hierarchy_url(country_code="AU"),
                          "/search/country/au/hierarchy/{0}".format(self.chapter.hierarchy_key))

    def test_chapter_has_5_child_headings(self):
        self.headings = mixer.cycle(5).blend(
            Heading,
            chapter=self.chapter
        )
        self.assertTrue(len(self.chapter.headings.all()) == 5)

    def test_chapter_has_child_headings(self):
        self.headings = mixer.cycle(5).blend(
            Heading,
            chapter=self.chapter
        )
        self.assertTrue(self.chapter.headings.all())

    def test_get_hierarchy_children_returns_list_of_child_items(self):
        """build a subsection of the structure"""
        section = mixer.blend(
            Section,
            section_id=10,
            roman_numeral=ROMAN_NUMERALS[1],
            tts_json="{}"
        )
        """create three chapters starting at 47 and attach to section 10"""
        chapters = mixer.cycle(3).blend(
            Chapter,
            tts_json="{}",
            section=section,
            chapter_code=seq(46)
        )
        """create 11 headings starting at 4901 and attached to chapter 49"""
        headings = mixer.cycle(11).blend(
            Heading,
            chapter=chapters[2],
            heading_code=(x for x in [4901000000, 4902000000, 4903000000, 4904000000, 4905000000, 4906000000,
                                      4907000000, 4908000000, 4909000000, 4910000000, 4911000000])
        )
        """create 6 subheadings starting at 4901 attached to heading 4901"""
        parent_subheadings = mixer.cycle(6).blend(
            SubHeading,
            heading=headings[0],
            commodity_code=(x for x in [4901000000, 4902000000, 4905000000, 4907000000, 4908000000, 4911000000])
        )
        """create 2 subheadings attached to subheading 4911"""
        subheadings = mixer.cycle(2).blend(
            SubHeading,
            parent_subheading=parent_subheadings[5],
            commodity_code=(x for x in [4911100000, 4911910000])
        )
        """create 1 subheading attached to subheading 491191"""
        sub_subheadings = mixer.cycle(1).blend(
            SubHeading,
            parent_subheading=subheadings[1],
            commodity_code=4911910000
        )
        """create 3 commodites attached to """
        commodities = mixer.cycle(3).blend(
            Commodity,
            parent_subheading=sub_subheadings[0],
            commodity_code=(x for x in [4911910010, 4911910090, 4911990000])
        )
        self.assertTrue(chapters[2].get_hierarchy_children())

        self.assertIn(parent_subheadings, [subheading.get_hierarchy_children() for subheading in headings])
        self.assertIn(subheadings, [subheading.get_hierarchy_children() for subheading in parent_subheadings])
        self.assertIn(sub_subheadings, [subheading.get_hierarchy_children() for subheading in subheadings])
        self.assertIn(commodities, [subheading.get_hierarchy_children() for subheading in sub_subheadings])


class HeadingTestCase(TestCase):
    """
    Test Heading Model
    """
    def setUp(self):
        self.heading = mixer.blend(
            Heading,
            tts_json="{}",
        )

        self.parent_subheadings = mixer.cycle(5).blend(
            SubHeading,
            heading=self.heading
        )

        self.heading_commodities = mixer.cycle(5).blend(
            Commodity,
            heading=self.heading
        )

    def test_str(self):
        self.assertEquals(str(self.heading), "Heading {0}".format(self.heading.heading_code))

    def test_hierarchy_key(self):
        self.assertEquals(self.heading.hierarchy_key, 'heading-{0}'.format(self.heading.pk))

    def test_hierarchy_url_without_country_code(self):
        self.assertRaises(NoReverseMatch, lambda: self.heading.get_hierarchy_url())

    def test_hierarchy_url_with_uppercased_country_code(self):
        self.assertEquals(self.heading.get_hierarchy_url(country_code="AU"),
                          "/search/country/au/hierarchy/{0}".format(self.heading.hierarchy_key))

    def test_tts_json_is_a_string_representing_an_empty_json_object(self):
        # TODO: remove field from Heading Model
        self.assertTrue(isinstance(self.heading.tts_json, str))
        self.assertEquals(self.heading.tts_json, "{}")

    def test_harmonized_code_equals_heading_code(self):
        # TODO: Where is this property method used
        self.assertEquals(self.heading.harmonized_code, self.heading.heading_code)

    def test_get_absolute_url(self):
        # TODO: remove from Heading model
        self.assertRaises(NoReverseMatch, lambda: self.heading.get_absolute_url())

    def test_hierarchy_url(self):
        self.assertEquals(self.heading.get_hierarchy_url(country_code="au"),
                          "/search/country/au/hierarchy/{0}".format(self.heading.hierarchy_key))

    def test_heading_has_child_subheadings(self):
        self.assertTrue(self.heading.child_subheadings.all())

    def test_heading_has_child_commodities(self):
        self.assertTrue(self.heading.children_concrete.all())

    def test_get_hierarchy_children_returns_list_of_child_items(self):
        self.assertTrue(self.heading.get_hierarchy_children())


class SubHeadingTestCase(TestCase):
    """
    Test Subheading Model
    """
    def setUp(self):

        self.heading = mixer.blend(
            Heading,
            tts_json="{}",
        )

        self.subheading = mixer.blend(
            SubHeading,
            tts_heading_json="{}",
            heading=self.heading
        )

        self.child_subheadings = mixer.cycle(5).blend(
            SubHeading,
            tts_heading_json="{}",
            parent_subheading=self.subheading
        )

        self.commodities = mixer.cycle(5).blend(
            Commodity,
            parent_subheading=self.subheading
        )

    def test_str(self):
        self.assertEquals(str(self.subheading), "Sub Heading {0}".format(self.subheading.commodity_code))

    def test_hierarchy_key(self):
        self.assertEquals(self.subheading.hierarchy_key, 'sub_heading-{0}'.format(self.subheading.pk))

    def test_tts_heading_json_is_a_string_representing_an_empty_json_object(self):
        # TODO: remove field from SubHeading Model
        self.assertTrue(isinstance(self.subheading.tts_heading_json, str))
        self.assertEquals(self.subheading.tts_heading_json, "{}")

    def test_harmonized_code_equals_commodity_code(self):
        # TODO: Where is this property method used
        self.assertEquals(self.subheading.harmonized_code, self.subheading.commodity_code)

    def test_get_parent(self):
        self.assertEquals(self.subheading.get_parent(), self.heading)
        self.assertEquals(self.child_subheadings[0].get_parent(), self.subheading)

    def test_hierarchy_url(self):
        self.assertEquals(self.subheading.get_hierarchy_url(country_code="au"),
                          "/search/country/au/hierarchy/{0}".format(self.subheading.hierarchy_key))

    def test_hierarchy_url_without_country_code(self):
        self.assertRaises(NoReverseMatch, lambda: self.subheading.get_hierarchy_url())

    def test_hierarchy_url_with_uppercased_country_code(self):
        self.assertEquals(self.subheading.get_hierarchy_url(country_code="AU"),
                          "/search/country/au/hierarchy/{0}".format(self.subheading.hierarchy_key))

    def test_subheading_has_child_subheadings(self):
        self.assertTrue(self.subheading.child_subheadings.all())

    def test_subheading_has_child_commodities(self):
        self.assertTrue(self.subheading.children_concrete.all())

    def test_get_hierarchy_children_returns_list_of_child_items(self):
        self.assertTrue(self.subheading.get_hierarchy_children())

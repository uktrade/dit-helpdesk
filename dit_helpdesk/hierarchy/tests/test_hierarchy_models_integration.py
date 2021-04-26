import json
import logging
from django.apps import apps
from django.conf import settings
from django.test import TestCase
from hierarchy.models import SubHeading, Heading, Section, Chapter
from hierarchy.helpers import create_nomenclature_tree

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


def create_instance(data, app_name, model_name):

    tts_json = data.pop("tts_json", None)
    model = apps.get_model(app_label=app_name, model_name=model_name)
    if tts_json:
        model.tts_json = tts_json

    instance = model(**data)
    instance.save()
    return instance


def get_data(file_path, tree):
    with open(file_path) as f:
        json_data = json.load(f)

    json_data["nomenclature_tree_id"] = tree.pk

    return json_data


class HierarchyModelsTestCase(TestCase):
    """
    test the integration between models that make up the full hierarchy
    """

    def setUp(self):
        """
        To fully test a commodity we need to load a parent subheading and its parent heading and save the
        relationships between the three model instances
        :return:
        """
        self.tree = create_nomenclature_tree(region="UK")
        self.section = create_instance(
            get_data(settings.SECTION_STRUCTURE, self.tree), "hierarchy", "Section"
        )

        self.chapter = create_instance(
            get_data(settings.CHAPTER_STRUCTURE, self.tree), "hierarchy", "Chapter"
        )
        self.chapter.section_id = self.chapter.pk
        self.chapter.save()

        self.heading = create_instance(
            get_data(settings.HEADING_STRUCTURE, self.tree), "hierarchy", "Heading"
        )
        self.heading.chapter_id = self.chapter.id
        self.heading.save()

        self.subheading = create_instance(
            get_data(settings.SUBHEADING_STRUCTURE, self.tree),
            "hierarchy",
            "SubHeading",
        )
        self.subheading.heading_id = self.heading.id
        self.subheading.save()

        self.commodity = create_instance(
            get_data(settings.COMMODITY_STRUCTURE, self.tree),
            "commodities",
            "Commodity",
        )
        self.commodity.parent_subheading_id = self.subheading.id
        self.commodity.tts_json = json.dumps(
            get_data(settings.COMMODITY_DATA, self.tree)
        )

        self.commodity.save()

    def test_section_instance_exists(self):
        self.assertTrue(Section.objects.get(section_id=settings.TEST_SECTION_ID))

    def test_self_section_is_and_instance_of_Section(self):
        self.assertTrue(isinstance(self.section, Section))

    def test_section_hierarchy_key_is_correct(self):
        self.assertEqual(
            self.section.hierarchy_key, "section-{0}".format(self.section.section_id)
        )

    def test_section_has_the_correct_hierarchy_url(self):
        self.assertEqual(
            self.section.get_hierarchy_url(settings.TEST_COUNTRY_CODE),
            "/search/country/au/hierarchy/section-{0}".format(self.section.section_id),
        )

    def test_section_has_hierarchy_children(self):
        children = self.section.get_hierarchy_children()
        child_count = self.section.get_hierarchy_children_count()
        self.assertTrue(len(children) > 0)
        self.assertTrue(child_count > 0)
        self.assertEqual(len(children), child_count)

    def test_section_has_child_chapters(self):
        self.assertTrue(self.section.chapter_range_str is not None)

    def test_section_has_child_chapters_str_is_a_string(self):
        # TODO: asdd more chapters to test correct string is returned
        self.assertTrue(isinstance(self.section.chapter_range_str, str))

    def test_section_title_is_correct(self):
        self.assertEqual(self.section.title, settings.TEST_SECTION_DESCRIPTION)

    def test_section_has_tts_obj(self):
        self.assertTrue(isinstance(self.section.tts_json, list))

    # Chapters
    def test_chapter_instance_exists(self):
        self.assertTrue(Chapter.objects.get(chapter_code=settings.TEST_CHAPTER_CODE))

    def test_self_chapter_is_and_instance_of_Chapter(self):
        self.assertTrue(isinstance(self.chapter, Chapter))

    def test_chapter_has_the_correct_title(self):
        self.assertTrue(self.chapter.title, settings.TEST_CHAPTER_DESCRIPTION)

    def test_chapter_has_the_correct_hierachy_key(self):
        self.assertEqual(
            self.chapter.hierarchy_key,
            "chapter-{0}".format(self.chapter.goods_nomenclature_sid),
        )

    def test_chapter_has_the_correct_harmonized_code(self):
        self.assertTrue(self.chapter.harmonized_code, settings.TEST_CHAPTER_CODE)

    def test_chapter_has_hierarchy_children(self):
        children = self.chapter.get_hierarchy_children()
        child_count = self.chapter.get_hierarchy_children_count()
        self.assertTrue(len(children) > 0)
        self.assertTrue(child_count > 0)
        self.assertEqual(len(children), child_count)

    def test_chapter_has_the_correct_hierarchy_url(self):
        self.assertEqual(
            self.chapter.get_hierarchy_url(settings.TEST_COUNTRY_CODE),
            "/search/country/au/hierarchy/chapter-{0}".format(
                self.chapter.goods_nomenclature_sid
            ),
        )

    # HEADINGS
    def test_heading_instance_exists(self):
        self.assertTrue(Heading.objects.get(heading_code=settings.TEST_HEADING_CODE))

    def test_self_heading_is_and_instance_of_Heading(self):
        self.assertTrue(isinstance(self.heading, Heading))

    def test_heading_instance_exists_with_short_code(self):
        self.assertTrue(Heading.objects.get(heading_code=settings.TEST_HEADING_CODE))

    def test_heading_has_the_correct_title(self):
        self.assertTrue(self.heading.description, settings.TEST_HEADING_DESCRIPTION)

    def test_heading_has_the_correct_hierachy_key(self):
        self.assertEqual(
            self.heading.hierarchy_key,
            "heading-{0}".format(self.heading.goods_nomenclature_sid),
        )

    def test_heading_has_tts_obj_is_an_instance_of_HeadingJson(self):
        # self.assertTrue(isinstance(self.heading.tts_obj, HeadingJson))
        self.assertEqual(self.heading.tts_json, None)

    def test_heading_has_the_correct_harmonized_code(self):
        self.assertTrue(self.heading.harmonized_code, settings.TEST_HEADING_CODE)

    def test_heading_has_hierarchy_children(self):
        children = self.heading.get_hierarchy_children()
        child_count = self.heading.get_hierarchy_children_count()
        self.assertTrue(len(children) > 0)
        self.assertTrue(child_count > 0)
        self.assertEqual(len(children), child_count)

    def test_heading_has_the_correct_hierarchy_url(self):
        self.assertEqual(
            self.heading.get_hierarchy_url(settings.TEST_COUNTRY_CODE),
            "/search/country/au/hierarchy/heading-{0}".format(
                self.heading.goods_nomenclature_sid
            ),
        )

    # SUBHEADINGS
    def test_subheading_instance_exists(self):
        self.assertTrue(
            SubHeading.objects.get(commodity_code=settings.TEST_SUBHEADING_CODE)
        )

    def test_self_subheading_is_and_instance_of_SubHeading(self):
        self.assertTrue(isinstance(self.subheading, SubHeading))

    def test_subheading_has_the_correct_title(self):
        self.assertTrue(
            self.subheading.description, settings.TEST_SUBHEADING_DESCRIPTION
        )

    def test_subheading_has_the_correct_hierachy_key(self):
        self.assertEqual(
            self.subheading.hierarchy_key,
            "sub_heading-{0}".format(self.subheading.goods_nomenclature_sid),
        )

    def test_subheading_has_the_correct_harmonized_code(self):
        self.assertTrue(self.subheading.harmonized_code, settings.TEST_SUBHEADING_CODE)

    def test_subheading_has_hierarchy_children(self):
        children = self.subheading.get_hierarchy_children()
        child_count = self.subheading.get_hierarchy_children_count()
        self.assertTrue(len(children) > 0)
        self.assertTrue(child_count > 0)
        self.assertEqual(len(children), child_count)

    def test_subheading_has_the_correct_hierarchy_url(self):
        self.assertEqual(
            self.subheading.get_hierarchy_url(settings.TEST_COUNTRY_CODE),
            "/search/country/au/hierarchy/sub_heading-{}".format(
                self.subheading.goods_nomenclature_sid
            ),
        )

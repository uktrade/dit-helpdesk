from mixer.backend.django import mixer

from django.test import TestCase

from commodities.models import Commodity
from hierarchy.models import (
    Chapter,
    Section,
    Heading,
    SubHeading,
)
from hierarchy.helpers import create_nomenclature_tree

from ..models import Regulation


class InheritedRegulationsTestCase(TestCase):
    """
    Test regulations manager inherited
    """

    def setUp(self):
        self.tree = create_nomenclature_tree('EU')

        self.model_classes = [
            Chapter,
            Section,
            Heading,
            SubHeading,
            Commodity,
        ]

        for model_class in self.model_classes:
            mixer.register(model_class, nomenclature_tree=self.tree)

    def test_models_without_regulations(self):

        for model_class in self.model_classes:
            obj = mixer.blend(model_class)
            self.assertFalse(obj.regulation_set.exists())
            regulations = Regulation.objects.inherited(obj)
            self.assertEqual(set(regulations), set([]))
            obj.delete()

    def test_model_with_regulation(self):
        model_classes = [
            (Chapter, 'chapters'),
            (Section, 'sections'),
            (Heading, 'headings'),
            (SubHeading, 'subheadings'),
            (Commodity, 'commodities'),
        ]

        for model_class, relation_attr in model_classes:
            obj = mixer.blend(model_class)
            a_regulation = mixer.blend(Regulation, **{relation_attr: obj})
            b_regulation = mixer.blend(Regulation, **{relation_attr: obj})
            self.assertEqual(obj.regulation_set.count(), 2)

            regulations = Regulation.objects.inherited(obj)
            self.assertEqual(set(regulations), set([a_regulation, b_regulation]))

            a_regulation.delete()
            b_regulation.delete()
            obj.delete()

    def test_models_in_one_level_hierarchy_single_regulation(self):
        heading = mixer.blend(Heading)
        regulation = mixer.blend(Regulation, headings=heading)
        commodity = mixer.blend(Commodity, heading=heading)

        commodity_regulations = Regulation.objects.inherited(commodity)
        self.assertEqual(set(commodity_regulations), set([regulation]))

        heading_regulations = Regulation.objects.inherited(heading)
        self.assertEqual(set(heading_regulations), set([regulation]))

    def test_models_multi_regulations_one_level_hierarchy(self):
        heading = mixer.blend(Heading)
        a_regulation = mixer.blend(Regulation, headings=heading)
        commodity = mixer.blend(Commodity, heading=heading)
        b_regulation = mixer.blend(Regulation, commodities=commodity)

        commodity_regulations = Regulation.objects.inherited(commodity)
        self.assertEqual(set(commodity_regulations), set([a_regulation, b_regulation]))

        heading_regulations = Regulation.objects.inherited(heading)
        self.assertEqual(set(heading_regulations), set([a_regulation]))

    def test_models_same_regulation_multiple_times_one_level_hierarchy(self):
        heading = mixer.blend(Heading)
        commodity = mixer.blend(Commodity, heading=heading)
        regulation = mixer.blend(Regulation, headings=heading, commodities=commodity)

        commodity_regulations = Regulation.objects.inherited(commodity)
        self.assertEqual(set(commodity_regulations), set([regulation]))

        heading_regulations = Regulation.objects.inherited(heading)
        self.assertEqual(set(heading_regulations), set([regulation]))

    def test_model_multi_level_hierarchy_one_regulation(self):
        section = mixer.blend(Section)
        regulation = mixer.blend(Regulation, sections=section)
        chapter = mixer.blend(Chapter, section=section)
        heading = mixer.blend(Heading, chapter=chapter)
        sub_heading = mixer.blend(SubHeading, heading=heading)
        commodity = mixer.blend(Commodity, parent_subheading=sub_heading)

        commodity_regulations = Regulation.objects.inherited(commodity)
        self.assertEqual(set(commodity_regulations), set([regulation]))

        sub_heading_regulations = Regulation.objects.inherited(sub_heading)
        self.assertEqual(set(sub_heading_regulations), set([regulation]))

        heading_regulations = Regulation.objects.inherited(heading)
        self.assertEqual(set(heading_regulations), set([regulation]))

        chapter_regulations = Regulation.objects.inherited(chapter)
        self.assertEqual(set(chapter_regulations), set([regulation]))

        section_regulations = Regulation.objects.inherited(section)
        self.assertEqual(set(section_regulations), set([regulation]))

    def test_model_multi_level_hierarchy_single_regulation(self):
        section = mixer.blend(Section)
        chapter = mixer.blend(Chapter, section=section)
        heading = mixer.blend(Heading, chapter=chapter)
        sub_heading = mixer.blend(SubHeading, heading=heading)
        commodity = mixer.blend(Commodity, parent_subheading=sub_heading)
        regulation = mixer.blend(
            Regulation,
            sections=section,
            chapters=chapter,
            headings=heading,
            sub_headings=sub_heading,
            commodities=commodity,
        )

        commodity_regulations = Regulation.objects.inherited(commodity)
        self.assertEqual(set(commodity_regulations), set([regulation]))

        sub_heading_regulations = Regulation.objects.inherited(sub_heading)
        self.assertEqual(set(sub_heading_regulations), set([regulation]))

        heading_regulations = Regulation.objects.inherited(heading)
        self.assertEqual(set(heading_regulations), set([regulation]))

        chapter_regulations = Regulation.objects.inherited(chapter)
        self.assertEqual(set(chapter_regulations), set([regulation]))

        section_regulations = Regulation.objects.inherited(section)
        self.assertEqual(set(section_regulations), set([regulation]))

    def get_model_multi_level_hierarchy_multiple_regulations(self):
        section = mixer.blend(Section)
        section_regulation = mixer.blend(Regulation, sections=section)
        chapter = mixer.blend(Chapter, section=section)
        chapter_regulation = mixer.blend(Regulation, chapters=chapter)
        heading = mixer.blend(Heading, chapter=chapter)
        heading_regulation = mixer.blend(Regulation, headings=heading)
        sub_heading = mixer.blend(SubHeading, heading=heading)
        sub_heading_regulation = mixer.blend(Regulation, sub_headings=sub_heading)
        commodity = mixer.blend(Commodity, parent_subheading=sub_heading)
        commodity_regulation = mixer.blend(Regulation, commodities=commodity)

        commodity_regulations = Regulation.objects.inherited(commodity)
        self.assertEqual(
            set(commodity_regulations),
            set([
                section_regulation,
                chapter_regulation,
                heading_regulation,
                sub_heading_regulation,
                commodity_regulation,
            ]),
        )

        sub_heading_regulations = Regulation.objects.inherited(sub_heading)
        self.assertEqual(
            set(sub_heading_regulations),
            set([
                section_regulation,
                chapter_regulation,
                heading_regulation,
                sub_heading_regulation,
            ]),
        )

        heading_regulations = Regulation.objects.inherited(heading)
        self.assertEqual(
            set(heading_regulations),
            set([
                section_regulation,
                chapter_regulation,
                heading_regulation,
            ]),
        )

        chapter_regulations = Regulation.objects.inherited(chapter)
        self.assertEqual(
            set(chapter_regulations),
            set([
                section_regulation,
                chapter_regulation,
            ]),
        )

        section_regulations = Regulation.objects.inherited(section)
        self.assertEqual(
            set(section_regulations),
            set([section_regulation]),
        )

    def test_regulations_in_multiple_hierarchies(self):
        a_commodity = mixer.blend(Commodity)
        a_regulation = mixer.blend(Regulation, commodities=a_commodity)

        b_commodity = mixer.blend(Commodity)
        b_regulation = mixer.blend(Regulation, commodities=b_commodity)

        a_commodity_regulations = Regulation.objects.inherited(a_commodity)
        self.assertEqual(
            set(a_commodity_regulations),
            set([a_regulation]),
        )

        b_commodity_regulations = Regulation.objects.inherited(b_commodity)
        self.assertEqual(
            set(b_commodity_regulations),
            set([b_regulation]),
        )

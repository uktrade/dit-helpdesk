from mixer.backend.django import Mixer

from django.test import TestCase

from commodities.models import Commodity
from hierarchy.models import Chapter, Section, Heading, SubHeading
from hierarchy.helpers import create_nomenclature_tree

from ..models import RegulationGroup


class InheritedRegulationGroupsTestCase(TestCase):
    """
    Test regulation groups manager inherited
    """

    def setUp(self):
        self.tree = create_nomenclature_tree("UK")

        self.model_classes = [Chapter, Section, Heading, SubHeading, Commodity]

        self.management_mixer = Mixer()

        for model_class in self.model_classes:
            self.management_mixer.register(model_class, nomenclature_tree=self.tree)

    def test_models_without_regulation_groups(self):

        for model_class in self.model_classes:
            obj = self.management_mixer.blend(model_class)
            self.assertFalse(obj.regulationgroup_set.exists())
            regulation_groups = RegulationGroup.objects.inherited(obj)
            self.assertEqual(set(regulation_groups), set([]))
            obj.delete()

    def test_model_with_regulation(self):
        model_classes = [
            (Chapter, "chapters"),
            (Section, "sections"),
            (Heading, "headings"),
            (SubHeading, "subheadings"),
            (Commodity, "commodities"),
        ]

        for model_class, relation_attr in model_classes:
            obj = self.management_mixer.blend(model_class)

            a_regulation = self.management_mixer.blend(
                RegulationGroup, **{relation_attr: obj}
            )
            b_regulation = self.management_mixer.blend(
                RegulationGroup, **{relation_attr: obj}
            )

            self.assertEqual(obj.regulationgroup_set.count(), 2)

            regulation_groups = RegulationGroup.objects.inherited(obj)
            self.assertEqual(set(regulation_groups), set([a_regulation, b_regulation]))

            a_regulation.delete()
            b_regulation.delete()
            obj.delete()

    def test_models_in_one_level_hierarchy_single_regulation(self):
        heading = self.management_mixer.blend(Heading)
        regulation = self.management_mixer.blend(RegulationGroup, headings=heading)
        commodity = self.management_mixer.blend(Commodity, heading=heading)

        commodity_regulation_groups = RegulationGroup.objects.inherited(commodity)
        self.assertEqual(set(commodity_regulation_groups), set([regulation]))

        heading_regulation_groups = RegulationGroup.objects.inherited(heading)
        self.assertEqual(set(heading_regulation_groups), set([regulation]))

    def test_models_multi_regulation_groups_one_level_hierarchy(self):
        heading = self.management_mixer.blend(Heading)
        commodity = self.management_mixer.blend(Commodity, heading=heading)

        a_regulation = self.management_mixer.blend(RegulationGroup, headings=heading)
        b_regulation = self.management_mixer.blend(
            RegulationGroup, commodities=commodity
        )

        commodity_regulation_groups = RegulationGroup.objects.inherited(commodity)
        self.assertEqual(
            set(commodity_regulation_groups), set([a_regulation, b_regulation])
        )

        heading_regulation_groups = RegulationGroup.objects.inherited(heading)
        self.assertEqual(set(heading_regulation_groups), set([a_regulation]))

    def test_models_same_regulation_multiple_times_one_level_hierarchy(self):
        heading = self.management_mixer.blend(Heading)
        commodity = self.management_mixer.blend(Commodity, heading=heading)
        regulation = self.management_mixer.blend(
            RegulationGroup, headings=heading, commodities=commodity
        )

        commodity_regulation_groups = RegulationGroup.objects.inherited(commodity)
        self.assertEqual(set(commodity_regulation_groups), set([regulation]))

        heading_regulation_groups = RegulationGroup.objects.inherited(heading)
        self.assertEqual(set(heading_regulation_groups), set([regulation]))

    def test_model_multi_level_hierarchy_one_regulation(self):
        section = self.management_mixer.blend(Section)
        regulation = self.management_mixer.blend(RegulationGroup, sections=section)
        chapter = self.management_mixer.blend(Chapter, section=section)
        heading = self.management_mixer.blend(Heading, chapter=chapter)
        sub_heading = self.management_mixer.blend(SubHeading, heading=heading)
        commodity = self.management_mixer.blend(
            Commodity, parent_subheading=sub_heading
        )

        commodity_regulation_groups = RegulationGroup.objects.inherited(commodity)
        self.assertEqual(set(commodity_regulation_groups), set([regulation]))

        sub_heading_regulation_groups = RegulationGroup.objects.inherited(sub_heading)
        self.assertEqual(set(sub_heading_regulation_groups), set([regulation]))

        heading_regulation_groups = RegulationGroup.objects.inherited(heading)
        self.assertEqual(set(heading_regulation_groups), set([regulation]))

        chapter_regulation_groups = RegulationGroup.objects.inherited(chapter)
        self.assertEqual(set(chapter_regulation_groups), set([regulation]))

        section_regulation_groups = RegulationGroup.objects.inherited(section)
        self.assertEqual(set(section_regulation_groups), set([regulation]))

    def test_model_multi_level_hierarchy_single_regulation(self):
        section = self.management_mixer.blend(Section)
        chapter = self.management_mixer.blend(Chapter, section=section)
        heading = self.management_mixer.blend(Heading, chapter=chapter)
        sub_heading = self.management_mixer.blend(SubHeading, heading=heading)
        commodity = self.management_mixer.blend(
            Commodity, parent_subheading=sub_heading
        )
        regulation = self.management_mixer.blend(
            RegulationGroup,
            sections=section,
            chapters=chapter,
            headings=heading,
            sub_headings=sub_heading,
            commodities=commodity,
        )

        commodity_regulation_groups = RegulationGroup.objects.inherited(commodity)
        self.assertEqual(set(commodity_regulation_groups), set([regulation]))

        sub_heading_regulation_groups = RegulationGroup.objects.inherited(sub_heading)
        self.assertEqual(set(sub_heading_regulation_groups), set([regulation]))

        heading_regulation_groups = RegulationGroup.objects.inherited(heading)
        self.assertEqual(set(heading_regulation_groups), set([regulation]))

        chapter_regulation_groups = RegulationGroup.objects.inherited(chapter)
        self.assertEqual(set(chapter_regulation_groups), set([regulation]))

        section_regulation_groups = RegulationGroup.objects.inherited(section)
        self.assertEqual(set(section_regulation_groups), set([regulation]))

    def get_model_multi_level_hierarchy_multiple_regulation_groups(self):
        section = self.management_mixer.blend(Section)
        section_regulation = self.management_mixer.blend(
            RegulationGroup, sections=section
        )

        chapter = self.management_mixer.blend(Chapter, section=section)
        chapter_regulation = self.management_mixer.blend(
            RegulationGroup, chapters=chapter
        )

        heading = self.management_mixer.blend(Heading, chapter=chapter)
        heading_regulation = self.management_mixer.blend(
            RegulationGroup, headings=heading
        )

        sub_heading = self.management_mixer.blend(SubHeading, heading=heading)
        sub_heading_regulation = self.management_mixer.blend(
            RegulationGroup, sub_headings=sub_heading
        )

        commodity = self.management_mixer.blend(
            Commodity, parent_subheading=sub_heading
        )
        commodity_regulation = self.management_mixer.blend(
            RegulationGroup, commodities=commodity
        )

        commodity_regulation_groups = RegulationGroup.objects.inherited(commodity)
        self.assertEqual(
            set(commodity_regulation_groups),
            set(
                [
                    section_regulation,
                    chapter_regulation,
                    heading_regulation,
                    sub_heading_regulation,
                    commodity_regulation,
                ]
            ),
        )

        sub_heading_regulation_groups = RegulationGroup.objects.inherited(sub_heading)
        self.assertEqual(
            set(sub_heading_regulation_groups),
            set(
                [
                    section_regulation,
                    chapter_regulation,
                    heading_regulation,
                    sub_heading_regulation,
                ]
            ),
        )

        heading_regulation_groups = RegulationGroup.objects.inherited(heading)
        self.assertEqual(
            set(heading_regulation_groups),
            set([section_regulation, chapter_regulation, heading_regulation]),
        )

        chapter_regulation_groups = RegulationGroup.objects.inherited(chapter)
        self.assertEqual(
            set(chapter_regulation_groups),
            set([section_regulation, chapter_regulation]),
        )

        section_regulation_groups = RegulationGroup.objects.inherited(section)
        self.assertEqual(set(section_regulation_groups), set([section_regulation]))

    def test_regulation_groups_in_multiple_hierarchies(self):
        a_commodity = self.management_mixer.blend(Commodity)
        a_regulation = self.management_mixer.blend(
            RegulationGroup, commodities=a_commodity
        )

        b_commodity = self.management_mixer.blend(Commodity)
        b_regulation = self.management_mixer.blend(
            RegulationGroup, commodities=b_commodity
        )

        a_commodity_regulation_groups = RegulationGroup.objects.inherited(a_commodity)
        self.assertEqual(set(a_commodity_regulation_groups), set([a_regulation]))

        b_commodity_regulation_groups = RegulationGroup.objects.inherited(b_commodity)
        self.assertEqual(set(b_commodity_regulation_groups), set([b_regulation]))

from mixer.backend.django import Mixer

from django.test import TestCase

from commodities.models import Commodity
from hierarchy.models import Chapter, Section, Heading, SubHeading
from hierarchy.helpers import create_nomenclature_tree

from ..hierarchy import replicate_regulation_groups
from ..models import RegulationGroup


class ReplicateRegulationGroupsTestCase(TestCase):
    """
    Test promote_regulation_groups
    """

    def setUp(self):
        self.tree = create_nomenclature_tree("UK")

        self.model_classes = [Chapter, Section, Heading, SubHeading, Commodity]

        self.mixer = Mixer()

        for model_class in self.model_classes:
            self.mixer.register(model_class, nomenclature_tree=self.tree)

    def test_models_without_regulations(self):
        for model_class in self.model_classes:
            obj = self.mixer.blend(model_class)
            self.assertFalse(obj.regulationgroup_set.exists())
            replicate_regulation_groups(obj)
            self.assertFalse(obj.regulationgroup_set.exists())
            obj.delete()

    def test_models_with_regulations(self):
        model_classes = [
            (Chapter, "chapters"),
            (Section, "sections"),
            (Heading, "headings"),
            (SubHeading, "subheadings"),
            (Commodity, "commodities"),
        ]

        for model_class, relation_attr in model_classes:
            obj = self.mixer.blend(model_class)
            regulation = self.mixer.blend(RegulationGroup, **{relation_attr: obj})

            replicate_regulation_groups(obj)
            self.assertEqual(obj.regulationgroup_set.count(), 1)
            self.assertEqual(obj.regulationgroup_set.first(), regulation)

            regulation.delete()
            obj.delete()

    def test_models_in_one_level_hierarchy_gets_replicated(self):
        """
        Test simple hierarchy

        Before:
        Heading    - <RegulationGroup: A>
           |
        Commodity  - No regulation

        After:
        Heading    - <RegulationGroup: A>
           |
        Commodity  - <RegulationGroup: A>
        """
        heading = self.mixer.blend(Heading)
        commodity = self.mixer.blend(Commodity, heading=heading)
        regulation = self.mixer.blend(RegulationGroup, headings=heading)

        self.assertTrue(heading.regulationgroup_set.exists())
        self.assertEqual(heading.regulationgroup_set.count(), 1)
        self.assertFalse(commodity.regulationgroup_set.exists())
        self.assertEqual(commodity.regulationgroup_set.count(), 0)

        replicate_regulation_groups(heading)

        self.assertEqual(heading.regulationgroup_set.count(), 1)
        self.assertEqual(heading.regulationgroup_set.first(), regulation)
        self.assertEqual(commodity.regulationgroup_set.count(), 1)
        self.assertEqual(commodity.regulationgroup_set.first(), regulation)

    def test_models_duplicated_in_one_level_hierarchy_gets_merged(self):
        """
        Test simple hierarchy

        Before:
        Heading    - <RegulationGroup: A>
           |
        Commodity  - <RegulationGroup: A>

        After:
        Heading    - <RegulationGroup: A>
           |
        Commodity  - <RegulationGroup: A>
        """
        heading = self.mixer.blend(Heading)
        commodity = self.mixer.blend(Commodity, heading=heading)
        regulation = self.mixer.blend(
            RegulationGroup, headings=heading, commodities=commodity
        )

        self.assertEqual(heading.regulationgroup_set.count(), 1)
        self.assertEqual(commodity.regulationgroup_set.count(), 1)

        replicate_regulation_groups(heading)

        self.assertEqual(heading.regulationgroup_set.count(), 1)
        self.assertEqual(heading.regulationgroup_set.first(), regulation)
        self.assertEqual(commodity.regulationgroup_set.count(), 1)
        self.assertEqual(commodity.regulationgroup_set.first(), regulation)

    def test_models_multi_children_in_one_level_hierarchy_gets_replicated(self):
        """
        Test simple hierarchy with multiple children

        Before:
                       Heading - <RegulationGroup: A>
                                 |
                   ______________________________
                  |                              |
        Commodity - No regulation    Commodity - No regulation

        After:
                       Heading - <RegulationGroup: A>
                                 |
                   ______________________________
                  |                              |
        Commodity - <RegulationGroup: A>    Commodity - <RegulationGroup: A>
        """
        heading = self.mixer.blend(Heading)
        a_commodity = self.mixer.blend(Commodity, heading=heading)
        b_commodity = self.mixer.blend(Commodity, heading=heading)
        regulation = self.mixer.blend(
            RegulationGroup,
            headings=heading,
        )

        self.assertEquals(heading.regulationgroup_set.count(), 1)
        self.assertFalse(a_commodity.regulationgroup_set.exists())
        self.assertFalse(b_commodity.regulationgroup_set.exists())

        replicate_regulation_groups(heading)

        self.assertEqual(heading.regulationgroup_set.count(), 1)
        self.assertEqual(heading.regulationgroup_set.first(), regulation)
        self.assertEqual(a_commodity.regulationgroup_set.count(), 1)
        self.assertEqual(a_commodity.regulationgroup_set.first(), regulation)
        self.assertEqual(b_commodity.regulationgroup_set.count(), 1)
        self.assertEqual(b_commodity.regulationgroup_set.first(), regulation)

    def test_models_multi_children_multi_regulations_in_one_level_hierarchy_gets_replicated(
        self,
    ):
        """
        Test simple hierarchy with multiple children multiple regulations

        Before:
                       Heading - <RegulationGroup: A>
                                 <RegulationGroup: B>
                                 |
                   ------------------------------
                  |                              |
        Commodity - No regulation    Commodity - No regulation

        After:
                       Heading - <RegulationGroup: A>
                                 <RegulationGroup: B>
                                 |
                   ------------------------------
                  |                              |
        Commodity - <RegulationGroup: A>    Commodity - <RegulationGroup: A>
                    <RegulationGroup: B>                <RegulationGroup: B>
        """
        heading = self.mixer.blend(Heading)
        a_commodity = self.mixer.blend(Commodity, heading=heading)
        b_commodity = self.mixer.blend(Commodity, heading=heading)
        a_regulation = self.mixer.blend(RegulationGroup, headings=heading)
        b_regulation = self.mixer.blend(RegulationGroup, headings=heading)

        self.assertEqual(heading.regulationgroup_set.count(), 2)
        self.assertFalse(a_commodity.regulationgroup_set.exists())
        self.assertFalse(b_commodity.regulationgroup_set.exists())

        replicate_regulation_groups(heading)

        self.assertEqual(heading.regulationgroup_set.count(), 2)
        self.assertIn(a_regulation, heading.regulationgroup_set.all())
        self.assertIn(b_regulation, heading.regulationgroup_set.all())
        self.assertEqual(a_commodity.regulationgroup_set.count(), 2)
        self.assertIn(a_regulation, a_commodity.regulationgroup_set.all())
        self.assertIn(b_regulation, a_commodity.regulationgroup_set.all())
        self.assertEqual(b_commodity.regulationgroup_set.count(), 2)
        self.assertIn(a_regulation, b_commodity.regulationgroup_set.all())
        self.assertIn(b_regulation, b_commodity.regulationgroup_set.all())

    def test_models_in_multi_level_hierarchy_gets_promoted(self):
        """
        Test multi level hierarchy

        Before:
        Chapter      - <RegulationGroup: A>
           |
        Section      - No RegulationGroup
           |
        Heading      - No RegulationGroup
           |
        SubHeading   - No RegulationGroup
           |
        Commodity    - No RegulationGroup

        After:
        Chapter      - <RegulationGroup: A>
           |
        Section      - <RegulationGroup: A>
           |
        Heading      - <RegulationGroup: A>
           |
        SubHeading   - <RegulationGroup: A>
           |
        Commodity    - <RegulationGroup: A>
        """
        section = self.mixer.blend(Section)
        chapter = self.mixer.blend(Chapter, section=section)
        heading = self.mixer.blend(Heading, chapter=chapter)
        sub_heading = self.mixer.blend(SubHeading, heading=heading)
        commodity = self.mixer.blend(Commodity, parent_subheading=sub_heading)
        regulation = self.mixer.blend(RegulationGroup, sections=section)

        self.assertEqual(section.regulationgroup_set.count(), 1)
        self.assertFalse(chapter.regulationgroup_set.exists())
        self.assertFalse(heading.regulationgroup_set.exists())
        self.assertFalse(sub_heading.regulationgroup_set.exists())
        self.assertFalse(commodity.regulationgroup_set.exists())

        replicate_regulation_groups(section)

        self.assertEqual(section.regulationgroup_set.count(), 1)
        self.assertEqual(section.regulationgroup_set.first(), regulation)
        self.assertEqual(chapter.regulationgroup_set.count(), 1)
        self.assertEqual(chapter.regulationgroup_set.first(), regulation)
        self.assertEqual(heading.regulationgroup_set.count(), 1)
        self.assertEqual(heading.regulationgroup_set.first(), regulation)
        self.assertEqual(sub_heading.regulationgroup_set.count(), 1)
        self.assertEqual(sub_heading.regulationgroup_set.first(), regulation)
        self.assertEqual(commodity.regulationgroup_set.count(), 1)
        self.assertEqual(commodity.regulationgroup_set.first(), regulation)

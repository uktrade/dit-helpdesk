from mixer.backend.django import mixer

from django.test import TestCase

from commodities.models import Commodity
from hierarchy.models import Chapter, Section, Heading, SubHeading
from hierarchy.helpers import create_nomenclature_tree

from ..hierarchy import promote_regulation_groups
from ..models import RegulationGroup


class PromoteRegulationGroupsTestCase(TestCase):
    """
    Test promote_regulation_groups
    """

    def setUp(self):
        self.tree = create_nomenclature_tree("UK")

        self.model_classes = [Chapter, Section, Heading, SubHeading, Commodity]

        for model_class in self.model_classes:
            mixer.register(model_class, nomenclature_tree=self.tree)

    def test_models_without_regulations(self):

        for model_class in self.model_classes:
            obj = mixer.blend(model_class)
            self.assertFalse(obj.regulationgroup_set.exists())
            promote_regulation_groups(obj)
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
            obj = mixer.blend(model_class)
            regulation = mixer.blend(RegulationGroup, **{relation_attr: obj})

            promote_regulation_groups(obj)
            self.assertEqual(obj.regulationgroup_set.count(), 1)
            self.assertEqual(obj.regulationgroup_set.first(), regulation)

            regulation.delete()
            obj.delete()

    def test_models_in_one_level_hierarchy_gets_promoted(self):
        """
        Test simple hierarchy

        Before:
        Heading    - No regulation
           |
        Commodity  - <RegulationGroup: A>

        After:
        Heading    - <RegulationGroup: A>
           |
        Commodity  - No regulation
        """
        heading = mixer.blend(Heading)
        commodity = mixer.blend(Commodity, heading=heading)
        regulation = mixer.blend(RegulationGroup, commodities=commodity)

        self.assertFalse(heading.regulationgroup_set.exists())
        self.assertEqual(commodity.regulationgroup_set.count(), 1)

        promote_regulation_groups(heading)

        self.assertEqual(heading.regulationgroup_set.count(), 1)
        self.assertEqual(heading.regulationgroup_set.first(), regulation)
        self.assertFalse(commodity.regulationgroup_set.exists())

    def test_models_multi_children_in_one_level_hierarchy_gets_promoted(self):
        """
        Test simple hierarchy with multiple children

        Before:
                       Heading - No regulation
                                 |
                   ______________________________
                  |                              |
        Commodity - <RegulationGroup: A>    Commodity - <RegulationGroup: A>

        After:
                       Heading - <RegulationGroup: A>
                                 |
                   ______________________________
                  |                              |
        Commodity - No regulation    Commodity - No regulation
        """
        heading = mixer.blend(Heading)
        a_commodity = mixer.blend(Commodity, heading=heading)
        b_commodity = mixer.blend(Commodity, heading=heading)
        regulation = mixer.blend(
            RegulationGroup, commodities=[a_commodity, b_commodity]
        )

        self.assertFalse(heading.regulationgroup_set.exists())
        self.assertEqual(a_commodity.regulationgroup_set.count(), 1)
        self.assertEqual(b_commodity.regulationgroup_set.count(), 1)

        promote_regulation_groups(heading)

        self.assertEqual(heading.regulationgroup_set.count(), 1)
        self.assertEqual(heading.regulationgroup_set.first(), regulation)
        self.assertFalse(a_commodity.regulationgroup_set.exists())
        self.assertFalse(b_commodity.regulationgroup_set.exists())

    def test_models_multi_children_multi_regulations_in_one_level_hierarchy_gets_promoted(
        self,
    ):
        """
        Test simple hierarchy with multiple children multiple regulations

        Before:
                       Heading - No regulation
                                 |
                   ------------------------------
                  |                              |
        Commodity - <RegulationGroup: A>    Commodity - <RegulationGroup: A>
                    <RegulationGroup: B>

        After:
                       Heading - <RegulationGroup: A>
                                 |
                   ------------------------------
                  |                              |
        Commodity - <RegulationGroup: B>    Commodity - No regulation
        """
        heading = mixer.blend(Heading)
        a_commodity = mixer.blend(Commodity, heading=heading)
        b_commodity = mixer.blend(Commodity, heading=heading)
        a_regulation = mixer.blend(
            RegulationGroup, commodities=[a_commodity, b_commodity]
        )
        b_regulation = mixer.blend(RegulationGroup, commodities=[a_commodity])

        self.assertFalse(heading.regulationgroup_set.exists())
        self.assertEqual(a_commodity.regulationgroup_set.count(), 2)
        self.assertEqual(b_commodity.regulationgroup_set.count(), 1)

        promote_regulation_groups(heading)

        self.assertEqual(heading.regulationgroup_set.count(), 1)
        self.assertEqual(heading.regulationgroup_set.first(), a_regulation)
        self.assertTrue(a_commodity.regulationgroup_set.count(), 1)
        self.assertEqual(a_commodity.regulationgroup_set.first(), b_regulation)
        self.assertFalse(b_commodity.regulationgroup_set.exists())

    def test_models_in_multi_level_hierarchy_gets_promoted(self):
        """
        Test multi level hierarchy

        Before:
        Chapter      - No RegulationGroup
           |
        Section      - No RegulationGroup
           |
        Heading      - No RegulationGroup
           |
        SubHeading   - No RegulationGroup
           |
        Commodity    - <RegulationGroup: A>

        After:
        Chapter      - <RegulationGroup: A>
           |
        Section      - No RegulationGroup
           |
        Heading      - No RegulationGroup
           |
        SubHeading   - No RegulationGroup
           |
        Commodity    - No RegulationGroup
        """
        section = mixer.blend(Section)
        chapter = mixer.blend(Chapter, section=section)
        heading = mixer.blend(Heading, chapter=chapter)
        sub_heading = mixer.blend(SubHeading, heading=heading)
        commodity = mixer.blend(Commodity, parent_subheading=sub_heading)
        regulation = mixer.blend(RegulationGroup, commodities=commodity)

        self.assertFalse(section.regulationgroup_set.exists())
        self.assertFalse(chapter.regulationgroup_set.exists())
        self.assertFalse(heading.regulationgroup_set.exists())
        self.assertFalse(sub_heading.regulationgroup_set.exists())
        self.assertEqual(commodity.regulationgroup_set.count(), 1)

        promote_regulation_groups(section)

        self.assertEqual(section.regulationgroup_set.count(), 1)
        self.assertEqual(section.regulationgroup_set.first(), regulation)
        self.assertFalse(chapter.regulationgroup_set.exists())
        self.assertFalse(heading.regulationgroup_set.exists())
        self.assertFalse(sub_heading.regulationgroup_set.exists())
        self.assertFalse(commodity.regulationgroup_set.exists())

    def test_models_multi_children_in_multi_level_hierarchy_gets_promoted(self):
        """
        Test multi children level hierarchy
        """
        section = mixer.blend(Section)

        a_chapter = mixer.blend(Chapter, section=section)
        b_chapter = mixer.blend(Chapter, section=section)
        chapters = [a_chapter, b_chapter]

        a_a_heading = mixer.blend(Heading, chapter=a_chapter)
        a_b_heading = mixer.blend(Heading, chapter=a_chapter)
        b_a_heading = mixer.blend(Heading, chapter=b_chapter)
        b_b_heading = mixer.blend(Heading, chapter=b_chapter)
        headings = [a_a_heading, a_b_heading, b_a_heading, b_b_heading]

        a_a_a_sub_heading = mixer.blend(SubHeading, heading=a_a_heading)
        a_a_b_sub_heading = mixer.blend(SubHeading, heading=a_a_heading)
        a_b_a_sub_heading = mixer.blend(SubHeading, heading=a_b_heading)
        a_b_b_sub_heading = mixer.blend(SubHeading, heading=a_b_heading)
        b_a_a_sub_heading = mixer.blend(SubHeading, heading=b_a_heading)
        b_a_b_sub_heading = mixer.blend(SubHeading, heading=b_a_heading)
        b_b_a_sub_heading = mixer.blend(SubHeading, heading=b_b_heading)
        b_b_b_sub_heading = mixer.blend(SubHeading, heading=b_b_heading)
        sub_headings = [
            a_a_a_sub_heading,
            a_a_b_sub_heading,
            a_b_a_sub_heading,
            a_b_b_sub_heading,
            b_a_a_sub_heading,
            b_a_b_sub_heading,
            b_b_a_sub_heading,
            b_b_b_sub_heading,
        ]

        a_a_a_a_commodity = mixer.blend(Commodity, parent_subheading=a_a_a_sub_heading)
        a_a_a_b_commodity = mixer.blend(Commodity, parent_subheading=a_a_a_sub_heading)
        a_a_b_a_commodity = mixer.blend(Commodity, parent_subheading=a_a_b_sub_heading)
        a_a_b_b_commodity = mixer.blend(Commodity, parent_subheading=a_a_b_sub_heading)
        a_b_a_a_commodity = mixer.blend(Commodity, parent_subheading=a_b_a_sub_heading)
        a_b_a_b_commodity = mixer.blend(Commodity, parent_subheading=a_b_a_sub_heading)
        a_b_b_a_commodity = mixer.blend(Commodity, parent_subheading=a_b_b_sub_heading)
        a_b_b_b_commodity = mixer.blend(Commodity, parent_subheading=a_b_b_sub_heading)
        b_a_a_a_commodity = mixer.blend(Commodity, parent_subheading=b_a_a_sub_heading)
        b_a_a_b_commodity = mixer.blend(Commodity, parent_subheading=b_a_a_sub_heading)
        b_a_b_a_commodity = mixer.blend(Commodity, parent_subheading=b_a_b_sub_heading)
        b_a_b_b_commodity = mixer.blend(Commodity, parent_subheading=b_a_b_sub_heading)
        b_b_a_a_commodity = mixer.blend(Commodity, parent_subheading=b_b_a_sub_heading)
        b_b_a_b_commodity = mixer.blend(Commodity, parent_subheading=b_b_a_sub_heading)
        b_b_b_a_commodity = mixer.blend(Commodity, parent_subheading=b_b_b_sub_heading)
        b_b_b_b_commodity = mixer.blend(Commodity, parent_subheading=b_b_b_sub_heading)
        commodities = [
            a_a_a_a_commodity,
            a_a_a_b_commodity,
            a_a_b_a_commodity,
            a_a_b_b_commodity,
            a_b_a_a_commodity,
            a_b_a_b_commodity,
            a_b_b_a_commodity,
            a_b_b_b_commodity,
            b_a_a_a_commodity,
            b_a_a_b_commodity,
            b_a_b_a_commodity,
            b_a_b_b_commodity,
            b_b_a_a_commodity,
            b_b_a_b_commodity,
            b_b_b_a_commodity,
            b_b_b_b_commodity,
        ]

        regulation = mixer.blend(
            RegulationGroup, commodities=[c.pk for c in commodities]
        )

        self.assertFalse(section.regulationgroup_set.exists())
        for chapter in chapters:
            self.assertFalse(chapter.regulationgroup_set.exists())
        for heading in headings:
            self.assertFalse(heading.regulationgroup_set.exists())
        for sub_heading in sub_headings:
            self.assertFalse(sub_heading.regulationgroup_set.exists())
        for commodity in commodities:
            self.assertEqual(commodity.regulationgroup_set.count(), 1)

        promote_regulation_groups(section)

        self.assertEqual(section.regulationgroup_set.count(), 1)
        self.assertEqual(section.regulationgroup_set.first(), regulation)
        for chapter in chapters:
            self.assertFalse(chapter.regulationgroup_set.exists())
        for heading in headings:
            self.assertFalse(heading.regulationgroup_set.exists())
        for sub_heading in sub_headings:
            self.assertFalse(sub_heading.regulationgroup_set.exists())
        for commodity in commodities:
            self.assertFalse(commodity.regulationgroup_set.exists())

    def test_models_multi_regulations_multi_children_in_multi_level_hierarchy_gets_promoted(
        self,
    ):
        """
        Test multi regulations and multi children level hierarchy
        """
        section = mixer.blend(Section)

        a_chapter = mixer.blend(Chapter, chapter_code="a", section=section)
        b_chapter = mixer.blend(Chapter, chapter_code="b", section=section)
        chapters = [a_chapter, b_chapter]

        a_a_heading = mixer.blend(Heading, heading_code="a_a", chapter=a_chapter)
        a_b_heading = mixer.blend(Heading, heading_code="a_b", chapter=a_chapter)
        b_a_heading = mixer.blend(Heading, heading_code="b_a", chapter=b_chapter)
        b_b_heading = mixer.blend(Heading, heading_code="b_b", chapter=b_chapter)
        headings = [a_a_heading, a_b_heading, b_a_heading, b_b_heading]

        a_a_a_sub_heading = mixer.blend(
            SubHeading, commodity_code="a_a_a", heading=a_a_heading
        )
        a_a_b_sub_heading = mixer.blend(
            SubHeading, commodity_code="a_a_b", heading=a_a_heading
        )
        a_b_a_sub_heading = mixer.blend(
            SubHeading, commodity_code="a_b_a", heading=a_b_heading
        )
        a_b_b_sub_heading = mixer.blend(
            SubHeading, commodity_code="a_b_b", heading=a_b_heading
        )
        b_a_a_sub_heading = mixer.blend(
            SubHeading, commodity_code="b_a_a", heading=b_a_heading
        )
        b_a_b_sub_heading = mixer.blend(
            SubHeading, commodity_code="b_a_b", heading=b_a_heading
        )
        b_b_a_sub_heading = mixer.blend(
            SubHeading, commodity_code="b_b_a", heading=b_b_heading
        )
        b_b_b_sub_heading = mixer.blend(
            SubHeading, commodity_code="b_b_b", heading=b_b_heading
        )
        sub_headings = [
            a_a_a_sub_heading,
            a_a_b_sub_heading,
            a_b_a_sub_heading,
            a_b_b_sub_heading,
            b_a_a_sub_heading,
            b_a_b_sub_heading,
            b_b_a_sub_heading,
            b_b_b_sub_heading,
        ]

        a_a_a_a_commodity = mixer.blend(
            Commodity, commodity_code="a_a_a_a", parent_subheading=a_a_a_sub_heading
        )
        a_a_a_b_commodity = mixer.blend(
            Commodity, commodity_code="a_a_a_b", parent_subheading=a_a_a_sub_heading
        )
        a_a_b_a_commodity = mixer.blend(
            Commodity, commodity_code="a_a_b_a", parent_subheading=a_a_b_sub_heading
        )
        a_a_b_b_commodity = mixer.blend(
            Commodity, commodity_code="a_a_b_b", parent_subheading=a_a_b_sub_heading
        )
        a_b_a_a_commodity = mixer.blend(
            Commodity, commodity_code="a_b_a_a", parent_subheading=a_b_a_sub_heading
        )
        a_b_a_b_commodity = mixer.blend(
            Commodity, commodity_code="a_b_a_b", parent_subheading=a_b_a_sub_heading
        )
        a_b_b_a_commodity = mixer.blend(
            Commodity, commodity_code="a_b_b_a", parent_subheading=a_b_b_sub_heading
        )
        a_b_b_b_commodity = mixer.blend(
            Commodity, commodity_code="a_b_b_b", parent_subheading=a_b_b_sub_heading
        )
        b_a_a_a_commodity = mixer.blend(
            Commodity, commodity_code="b_a_a_a", parent_subheading=b_a_a_sub_heading
        )
        b_a_a_b_commodity = mixer.blend(
            Commodity, commodity_code="b_a_a_b", parent_subheading=b_a_a_sub_heading
        )
        b_a_b_a_commodity = mixer.blend(
            Commodity, commodity_code="b_a_b_a", parent_subheading=b_a_b_sub_heading
        )
        b_a_b_b_commodity = mixer.blend(
            Commodity, commodity_code="b_a_b_b", parent_subheading=b_a_b_sub_heading
        )
        b_b_a_a_commodity = mixer.blend(
            Commodity, commodity_code="b_b_a_a", parent_subheading=b_b_a_sub_heading
        )
        b_b_a_b_commodity = mixer.blend(
            Commodity, commodity_code="b_b_a_b", parent_subheading=b_b_a_sub_heading
        )
        b_b_b_a_commodity = mixer.blend(
            Commodity, commodity_code="b_b_b_a", parent_subheading=b_b_b_sub_heading
        )
        b_b_b_b_commodity = mixer.blend(
            Commodity, commodity_code="b_b_b_b", parent_subheading=b_b_b_sub_heading
        )
        commodities = [
            a_a_a_a_commodity,
            a_a_a_b_commodity,
            a_a_b_a_commodity,
            a_a_b_b_commodity,
            a_b_a_a_commodity,
            a_b_a_b_commodity,
            a_b_b_a_commodity,
            a_b_b_b_commodity,
            b_a_a_a_commodity,
            b_a_a_b_commodity,
            b_a_b_a_commodity,
            b_a_b_b_commodity,
            b_b_a_a_commodity,
            b_b_a_b_commodity,
            b_b_b_a_commodity,
            b_b_b_b_commodity,
        ]

        a_regulation_commodities = commodities
        a_regulation = mixer.blend(
            RegulationGroup,
            title="a_regulation",
            commodities=[c.pk for c in a_regulation_commodities],
        )
        b_regulation_commodities = commodities[:8]
        b_regulation = mixer.blend(
            RegulationGroup,
            title="b_regulation",
            commodities=[c.pk for c in b_regulation_commodities],
        )
        c_regulation_commodities = commodities[:4]
        c_regulation = mixer.blend(
            RegulationGroup,
            title="c_regulation",
            commodities=[c.pk for c in c_regulation_commodities],
        )
        d_regulation_commodities = commodities[:2]
        d_regulation = mixer.blend(
            RegulationGroup,
            title="d_regulation",
            commodities=[c.pk for c in d_regulation_commodities],
        )
        e_regulation_commodities = commodities[:1]
        e_regulation = mixer.blend(
            RegulationGroup,
            title="e_regulation",
            commodities=[c.pk for c in e_regulation_commodities],
        )

        promote_regulation_groups(section)

        self.assertEqual(section.regulationgroup_set.count(), 1)
        self.assertEqual(section.regulationgroup_set.first(), a_regulation)

        self.assertEqual(a_chapter.regulationgroup_set.count(), 1)
        self.assertEqual(a_chapter.regulationgroup_set.first(), b_regulation)
        self.assertFalse(b_chapter.regulationgroup_set.exists())

        self.assertEqual(a_a_heading.regulationgroup_set.count(), 1)
        self.assertEqual(a_a_heading.regulationgroup_set.first(), c_regulation)
        for heading in headings[1:]:
            self.assertFalse(heading.regulationgroup_set.exists())

        self.assertEqual(a_a_a_sub_heading.regulationgroup_set.count(), 1)
        self.assertEqual(a_a_a_sub_heading.regulationgroup_set.first(), d_regulation)
        for sub_heading in sub_headings[1:]:
            self.assertFalse(sub_heading.regulationgroup_set.exists())

        self.assertEqual(a_a_a_a_commodity.regulationgroup_set.count(), 1)
        self.assertEqual(a_a_a_a_commodity.regulationgroup_set.first(), e_regulation)
        for commodity in commodities[1:]:
            self.assertFalse(commodity.regulationgroup_set.exists())

    def test_models_in_simple_sub_heading_hierarchy_gets_promoted(self):
        """
        Test simple sub heading hierarchy

        Before:
        Sub Heading    - No regulation
           |
        Sub Heading    - No regulation
           |
        Commodity      - <RegulationGroup: A>

        After:
        Sub Heading    - <RegulationGroup: A>
           |
        Sub Heading    - No regulation
           |
        Commodity  - No regulation
        """
        a_sub_heading = mixer.blend(SubHeading)
        b_sub_heading = mixer.blend(SubHeading, parent_subheading=a_sub_heading)
        commodity = mixer.blend(Commodity, parent_subheading=b_sub_heading)
        regulation = mixer.blend(RegulationGroup, commodities=commodity)

        self.assertFalse(a_sub_heading.regulationgroup_set.exists())
        self.assertFalse(b_sub_heading.regulationgroup_set.exists())
        self.assertEqual(commodity.regulationgroup_set.count(), 1)

        promote_regulation_groups(a_sub_heading)

        self.assertEqual(a_sub_heading.regulationgroup_set.count(), 1)
        self.assertEqual(a_sub_heading.regulationgroup_set.first(), regulation)
        self.assertFalse(b_sub_heading.regulationgroup_set.exists())
        self.assertFalse(commodity.regulationgroup_set.exists())

    def test_models_in_simple_sub_heading_and_heading_hierarchy_gets_promoted(self):
        """
        Test simple sub heading hierarchy

        Before:
        Heading        - No regulation
           |
        Sub Heading    - No regulation
           |
        Sub Heading    - No regulation
           |
        Commodity      - <RegulationGroup: A>

        After:
        Heading        - <RegulationGroup: A>
           |
        Sub Heading    - No regulation
           |
        Sub Heading    - No regulation
           |
        Commodity  - No regulation
        """
        heading = mixer.blend(Heading)
        a_sub_heading = mixer.blend(SubHeading, heading=heading)
        b_sub_heading = mixer.blend(SubHeading, parent_subheading=a_sub_heading)
        commodity = mixer.blend(Commodity, parent_subheading=b_sub_heading)
        regulation = mixer.blend(RegulationGroup, commodities=commodity)

        self.assertFalse(a_sub_heading.regulationgroup_set.exists())
        self.assertFalse(b_sub_heading.regulationgroup_set.exists())
        self.assertEqual(commodity.regulationgroup_set.count(), 1)

        promote_regulation_groups(heading)

        self.assertEqual(heading.regulationgroup_set.count(), 1)
        self.assertEqual(heading.regulationgroup_set.first(), regulation)
        self.assertFalse(a_sub_heading.regulationgroup_set.exists())
        self.assertFalse(b_sub_heading.regulationgroup_set.exists())
        self.assertFalse(commodity.regulationgroup_set.exists())

from mixer.backend.django import mixer

from django.test import TestCase

from commodities.models import Commodity
from hierarchy.models import (
    Chapter,
    Section,
    Heading,
    SubHeading,
)

from ..hierarchy import promote_regulations
from ..models import Regulation


class PromoteRegulationsTestCase(TestCase):
    """
    Test promote_regulations
    """

    def test_models_without_regulations(self):
        model_classes = [
            Chapter,
            Section,
            Heading,
            SubHeading,
            Commodity,
        ]

        for model_class in model_classes:
            obj = mixer.blend(model_class)
            self.assertFalse(obj.regulation_set.exists())
            promote_regulations(obj)
            self.assertFalse(obj.regulation_set.exists())
            obj.delete()

    def test_models_with_regulations(self):
        model_classes = [
            (Chapter, 'chapters'),
            (Section, 'sections'),
            (Heading, 'headings'),
            (SubHeading, 'subheadings'),
            (Commodity, 'commodities'),
        ]

        for model_class, relation_attr in model_classes:
            obj = mixer.blend(model_class)
            regulation = mixer.blend(Regulation, **{relation_attr: obj})

            promote_regulations(obj)
            self.assertEqual(obj.regulation_set.count(), 1)
            self.assertEqual(obj.regulation_set.first(), regulation)

            regulation.delete()
            obj.delete()

    def test_models_in_one_level_hierarchy_gets_promoted(self):
        """
        Test simple hierarchy

        Before:
        Heading    - No regulation
           |
        Commodity  - <Regulation: A>

        After:
        Heading    - <Regulation: A>
           |
        Commodity  - <Regulation: A>
        """
        heading = mixer.blend(Heading)
        commodity = mixer.blend(Commodity, heading=heading)
        regulation = mixer.blend(Regulation, commodities=commodity)

        self.assertFalse(heading.regulation_set.exists())
        self.assertEqual(commodity.regulation_set.count(), 1)

        promote_regulations(heading)

        self.assertEqual(heading.regulation_set.count(), 1)
        self.assertEqual(heading.regulation_set.first(), regulation)
        self.assertTrue(commodity.regulation_set.count(), 1)
        self.assertEqual(commodity.regulation_set.first(), regulation)

    def test_models_in_multi_level_hierarchy_gets_promoted(self):
        """
        Test multi level hierarchy

        Before:
        Chapter      - No Regulation
           |
        Section      - No Regulation
           |
        Heading      - No Regulation
           |
        SubHeading   - No Regulation
           |
        Commodity    - <Regulation: A>

        After:
        Chapter      - <Regulation: A>
           |
        Section      - <Regulation: A>
           |
        Heading      - <Regulation: A>
           |
        SubHeading   - <Regulation: A>
           |
        Commodity    - <Regulation: A>
        """
        section = mixer.blend(Section)
        chapter = mixer.blend(Chapter, section=section)
        heading = mixer.blend(Heading, chapter=chapter)
        sub_heading = mixer.blend(SubHeading, heading=heading)
        commodity = mixer.blend(Commodity, parent_subheading=sub_heading)
        regulation = mixer.blend(Regulation, commodities=commodity)

        self.assertFalse(section.regulation_set.exists())
        self.assertFalse(chapter.regulation_set.exists())
        self.assertFalse(heading.regulation_set.exists())
        self.assertFalse(sub_heading.regulation_set.exists())
        self.assertEqual(commodity.regulation_set.count(), 1)

        promote_regulations(section)

        self.assertEqual(section.regulation_set.count(), 1)
        self.assertEqual(section.regulation_set.first(), regulation)
        self.assertEqual(chapter.regulation_set.count(), 1)
        self.assertEqual(chapter.regulation_set.first(), regulation)
        self.assertEqual(heading.regulation_set.count(), 1)
        self.assertEqual(heading.regulation_set.first(), regulation)
        self.assertEqual(sub_heading.regulation_set.count(), 1)
        self.assertEqual(sub_heading.regulation_set.first(), regulation)
        self.assertEqual(commodity.regulation_set.count(), 1)
        self.assertEqual(commodity.regulation_set.first(), regulation)

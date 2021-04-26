from mixer.backend.django import mixer

from django.test import TestCase

from commodities.models import Commodity

from ..helpers import create_nomenclature_tree, permute_code_hierarchy
from ..models import Section, Chapter, Heading, SubHeading


class PermuteCodeHierarchyTestCase(TestCase):
    def test_permute_code_hierarchy(self):
        tree = create_nomenclature_tree("UK")
        section = mixer.blend(Section, nomenclature_tree=tree)
        chapter = mixer.blend(
            Chapter, nomenclature_tree=tree, section=section, chapter_code="12"
        )
        heading = mixer.blend(
            Heading, nomenclature_tree=tree, chapter=chapter, heading_code="1234"
        )
        sub_heading_1 = mixer.blend(
            SubHeading, nomenclature_tree=tree, heading=heading, commodity_code="123456"
        )
        sub_heading_2 = mixer.blend(
            SubHeading,
            nomenclature_tree=tree,
            parent_subheading=sub_heading_1,
            commodity_code="12345678",
        )
        commodity = mixer.blend(
            Commodity,
            nomenclature_tree=tree,
            parent_subheading=sub_heading_2,
            commodity_code="1234567890",
        )

        generator = permute_code_hierarchy(commodity)
        self.assertEqual(next(generator), "1234567890")
        self.assertEqual(next(generator), "12345678")
        self.assertEqual(next(generator), "123456")
        self.assertEqual(next(generator), "1234")
        self.assertEqual(next(generator), "12")
        with self.assertRaises(StopIteration):
            next(generator)

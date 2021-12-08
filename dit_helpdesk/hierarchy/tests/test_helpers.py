from mixer.backend.django import mixer

from django.test import TestCase

from commodities.models import Commodity

from datetime import datetime, timedelta

from ..helpers import (
    create_nomenclature_tree,
    permute_code_hierarchy,
    delete_outdated_trees,
)
from ..models import NomenclatureTree, Section, Chapter, Heading, SubHeading


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


class DeleteOutdatedTreesTestCase(TestCase):
    def setUp(self):

        last_active_end_date = datetime.now()
        outdated_end_date = datetime.now() - timedelta(days=1)

        self.active_uk_tree = mixer.blend(NomenclatureTree, region="UK", end_date=None)
        self.active_eu_tree = mixer.blend(NomenclatureTree, region="EU", end_date=None)
        self.last_active_uk_tree = mixer.blend(
            NomenclatureTree, region="UK", end_date=last_active_end_date
        )
        self.last_active_eu_tree = mixer.blend(
            NomenclatureTree, region="EU", end_date=last_active_end_date
        )
        self.outdated_uk_tree = mixer.blend(
            NomenclatureTree, region="UK", end_date=outdated_end_date
        )
        self.outdated_eu_tree = mixer.blend(
            NomenclatureTree, region="EU", end_date=outdated_end_date
        )

    def test_delete_outdated_trees(self):

        delete_outdated_trees()

        trees_table_contents = NomenclatureTree.objects.all()
        # Check the tree table contains the self.active trees
        self.assertIn(self.active_uk_tree, trees_table_contents)
        self.assertIn(self.active_eu_tree, trees_table_contents)
        # Check the tree table contains the self.last_active trees
        self.assertIn(self.last_active_uk_tree, trees_table_contents)
        self.assertIn(self.last_active_eu_tree, trees_table_contents)
        # Check the tree table is missing the self.outdated trees
        self.assertNotIn(self.outdated_uk_tree, trees_table_contents)
        self.assertNotIn(self.outdated_eu_tree, trees_table_contents)

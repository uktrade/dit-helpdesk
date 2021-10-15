import sys

from mixer.backend.django import mixer

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from commodities.models import Commodity
from hierarchy.helpers import create_nomenclature_tree
from hierarchy.models import Chapter, Heading, NomenclatureTree, Section, SubHeading
from regulations.models import Regulation, RegulationGroup


class MigrateRegulationsTest(TestCase):
    def setUp(self) -> None:
        self.tree = create_nomenclature_tree()
        self.new_tree = NomenclatureTree.objects.create(
            region="UK", start_date=timezone.now(), end_date=timezone.now()
        )

    def test_migrate_regulation_groups(self):
        regulation_group = mixer.blend(RegulationGroup)
        regulation_group.nomenclature_trees.add(self.tree)
        regulation_group.save()

        call_command("migrate_regulations", stdout=sys.stdout)

        self.assertIn(self.new_tree, regulation_group.nomenclature_trees.all())
        self.assertEqual(self.new_tree.regulationgroup_set.count(), 1)

    def test_previous_tree_has_no_regulation_groups(self):
        regulation_group = mixer.blend(RegulationGroup)

        self.assertEqual(self.tree.regulationgroup_set.count(), 0)
        self.assertEqual(RegulationGroup.objects.count(), 1)

        call_command("migrate_regulations", stdout=sys.stdout)

        self.assertEqual(self.tree.regulationgroup_set.count(), 0)
        self.assertIn(self.new_tree, regulation_group.nomenclature_trees.all())
        self.assertEqual(self.new_tree.regulationgroup_set.count(), 1)

    def test_previous_tree_has_no_regulations(self):
        regulation = mixer.blend(Regulation)

        self.assertEqual(self.tree.regulation_set.count(), 0)
        self.assertEqual(Regulation.objects.count(), 1)

        call_command("migrate_regulations", stdout=sys.stdout)

        self.assertEqual(self.tree.regulation_set.count(), 0)
        self.assertIn(self.new_tree, regulation.nomenclature_trees.all())
        self.assertEqual(self.new_tree.regulation_set.count(), 1)

    def test_migrate_commodity_regulation_groups(self):
        commodity = mixer.blend(Commodity, nomenclature_tree=self.tree)

        regulation_group = mixer.blend(RegulationGroup, commodities=commodity)
        regulation_group.nomenclature_trees.add(self.tree)
        regulation_group.save()

        another_regulation_group = mixer.blend(RegulationGroup, commodities=commodity)
        another_regulation_group.nomenclature_trees.add(self.tree)
        another_regulation_group.save()

        new_commodity = mixer.blend(
            Commodity,
            goods_nomenclature_sid=commodity.goods_nomenclature_sid,
            nomenclature_tree=self.new_tree,
        )

        call_command("migrate_regulations", stdout=sys.stdout)

        self.assertIn(regulation_group, new_commodity.regulationgroup_set.all())
        self.assertIn(another_regulation_group, new_commodity.regulationgroup_set.all())
        self.assertEqual(new_commodity.regulationgroup_set.count(), 2)

    def test_migrate_regulation_groups_commodity_contracts_to_subheading(self):
        commodity = mixer.blend(Commodity, nomenclature_tree=self.tree)

        regulation_group = mixer.blend(RegulationGroup, commodities=commodity)
        regulation_group.nomenclature_trees.add(self.tree)
        regulation_group.save()

        another_regulation_group = mixer.blend(RegulationGroup, commodities=commodity)
        another_regulation_group.nomenclature_trees.add(self.tree)
        another_regulation_group.save()

        new_subheading = mixer.blend(
            SubHeading,
            goods_nomenclature_sid=commodity.goods_nomenclature_sid,
            nomenclature_tree=self.new_tree,
        )

        call_command("migrate_regulations", stdout=sys.stdout)

        self.assertIn(regulation_group, new_subheading.regulationgroup_set.all())
        self.assertIn(
            another_regulation_group, new_subheading.regulationgroup_set.all()
        )
        self.assertEqual(new_subheading.regulationgroup_set.count(), 2)

    def test_migrate_subheading_regulation_groups(self):
        subheading = mixer.blend(SubHeading, nomenclature_tree=self.tree)

        regulation_group = mixer.blend(RegulationGroup, subheadings=subheading)
        regulation_group.nomenclature_trees.add(self.tree)
        regulation_group.save()

        another_regulation_group = mixer.blend(RegulationGroup, subheadings=subheading)
        another_regulation_group.nomenclature_trees.add(self.tree)
        another_regulation_group.save()

        new_subheading = mixer.blend(
            SubHeading,
            goods_nomenclature_sid=subheading.goods_nomenclature_sid,
            nomenclature_tree=self.new_tree,
        )

        call_command("migrate_regulations", stdout=sys.stdout)

        self.assertIn(regulation_group, new_subheading.regulationgroup_set.all())
        self.assertIn(
            another_regulation_group, new_subheading.regulationgroup_set.all()
        )
        self.assertEqual(new_subheading.regulationgroup_set.count(), 2)

    def test_migrate_regulation_groups_subheading_expands_to_commodity(self):
        subheading = mixer.blend(SubHeading, nomenclature_tree=self.tree)

        regulation_group = mixer.blend(RegulationGroup, subheadings=subheading)
        regulation_group.nomenclature_trees.add(self.tree)
        regulation_group.save()

        another_regulation_group = mixer.blend(RegulationGroup, subheadings=subheading)
        another_regulation_group.nomenclature_trees.add(self.tree)
        another_regulation_group.save()

        new_commodity = mixer.blend(
            Commodity,
            goods_nomenclature_sid=subheading.goods_nomenclature_sid,
            nomenclature_tree=self.new_tree,
        )

        call_command("migrate_regulations", stdout=sys.stdout)

        self.assertIn(regulation_group, new_commodity.regulationgroup_set.all())
        self.assertIn(another_regulation_group, new_commodity.regulationgroup_set.all())
        self.assertEqual(new_commodity.regulationgroup_set.count(), 2)

    def test_migrate_regulation_groups_subheading_contracts_to_chapter(self):
        subheading = mixer.blend(SubHeading, nomenclature_tree=self.tree)

        regulation_group = mixer.blend(RegulationGroup, subheadings=subheading)
        regulation_group.nomenclature_trees.add(self.tree)
        regulation_group.save()

        another_regulation_group = mixer.blend(RegulationGroup, subheadings=subheading)
        another_regulation_group.nomenclature_trees.add(self.tree)
        another_regulation_group.save()

        new_chapter = mixer.blend(
            Chapter,
            goods_nomenclature_sid=subheading.goods_nomenclature_sid,
            nomenclature_tree=self.new_tree,
        )

        call_command("migrate_regulations", stdout=sys.stdout)

        self.assertIn(regulation_group, new_chapter.regulationgroup_set.all())
        self.assertIn(another_regulation_group, new_chapter.regulationgroup_set.all())
        self.assertEqual(new_chapter.regulationgroup_set.count(), 2)

    def test_migrate_heading_regulation_groups(self):
        heading = mixer.blend(Heading, nomenclature_tree=self.tree)

        regulation_group = mixer.blend(RegulationGroup, headings=heading)
        regulation_group.nomenclature_trees.add(self.tree)
        regulation_group.save()

        another_regulation_group = mixer.blend(RegulationGroup, headings=heading)
        another_regulation_group.nomenclature_trees.add(self.tree)
        another_regulation_group.save()

        new_heading = mixer.blend(
            Heading,
            goods_nomenclature_sid=heading.goods_nomenclature_sid,
            nomenclature_tree=self.new_tree,
        )

        call_command("migrate_regulations", stdout=sys.stdout)

        self.assertIn(regulation_group, new_heading.regulationgroup_set.all())
        self.assertIn(another_regulation_group, new_heading.regulationgroup_set.all())
        self.assertEqual(new_heading.regulationgroup_set.count(), 2)

    def test_migrate_regulation_groups_heading_expands_to_subheading(self):
        heading = mixer.blend(Heading, nomenclature_tree=self.tree)

        regulation_group = mixer.blend(RegulationGroup, headings=heading)
        regulation_group.nomenclature_trees.add(self.tree)
        regulation_group.save()

        another_regulation_group = mixer.blend(RegulationGroup, headings=heading)
        another_regulation_group.nomenclature_trees.add(self.tree)
        another_regulation_group.save()

        new_subheading = mixer.blend(
            SubHeading,
            goods_nomenclature_sid=heading.goods_nomenclature_sid,
            nomenclature_tree=self.new_tree,
        )

        call_command("migrate_regulations", stdout=sys.stdout)

        self.assertIn(regulation_group, new_subheading.regulationgroup_set.all())
        self.assertIn(
            another_regulation_group, new_subheading.regulationgroup_set.all()
        )
        self.assertEqual(new_subheading.regulationgroup_set.count(), 2)

    def test_migrate_chapters_regulation_groups(self):
        chapter = mixer.blend(
            Chapter,
            nomenclature_tree=self.tree,
        )

        regulation_group = mixer.blend(RegulationGroup, chapters=chapter)
        regulation_group.nomenclature_trees.add(self.tree)
        regulation_group.save()

        another_regulation_group = mixer.blend(RegulationGroup, chapters=chapter)
        another_regulation_group.nomenclature_trees.add(self.tree)
        another_regulation_group.save()

        new_chapter = mixer.blend(
            Chapter,
            goods_nomenclature_sid=chapter.goods_nomenclature_sid,
            nomenclature_tree=self.new_tree,
        )

        call_command("migrate_regulations", stdout=sys.stdout)

        self.assertIn(regulation_group, new_chapter.regulationgroup_set.all())
        self.assertIn(another_regulation_group, new_chapter.regulationgroup_set.all())
        self.assertEqual(new_chapter.regulationgroup_set.count(), 2)

    def test_migrate_regulation_groups_chapter_expands_to_subheading(self):
        chapter = mixer.blend(
            Chapter,
            nomenclature_tree=self.tree,
        )

        regulation_group = mixer.blend(RegulationGroup, chapters=chapter)
        regulation_group.nomenclature_trees.add(self.tree)
        regulation_group.save()

        another_regulation_group = mixer.blend(RegulationGroup, chapters=chapter)
        another_regulation_group.nomenclature_trees.add(self.tree)
        another_regulation_group.save()

        new_subheading = mixer.blend(
            SubHeading,
            goods_nomenclature_sid=chapter.goods_nomenclature_sid,
            nomenclature_tree=self.new_tree,
        )

        call_command("migrate_regulations", stdout=sys.stdout)

        self.assertIn(regulation_group, new_subheading.regulationgroup_set.all())
        self.assertIn(
            another_regulation_group, new_subheading.regulationgroup_set.all()
        )
        self.assertEqual(new_subheading.regulationgroup_set.count(), 2)

    def test_migrate_sections_regulation_groups(self):
        section = mixer.blend(Section, nomenclature_tree=self.tree)

        regulation_group = mixer.blend(RegulationGroup, sections=section)
        regulation_group.nomenclature_trees.add(self.tree)
        regulation_group.save()

        another_regulation_group = mixer.blend(RegulationGroup, sections=section)
        another_regulation_group.nomenclature_trees.add(self.tree)
        another_regulation_group.save()

        new_section = mixer.blend(
            Section,
            roman_numeral=section.roman_numeral,
            nomenclature_tree=self.new_tree,
        )

        call_command("migrate_regulations", stdout=sys.stdout)

        self.assertIn(regulation_group, new_section.regulationgroup_set.all())
        self.assertIn(another_regulation_group, new_section.regulationgroup_set.all())
        self.assertEqual(new_section.regulationgroup_set.count(), 2)

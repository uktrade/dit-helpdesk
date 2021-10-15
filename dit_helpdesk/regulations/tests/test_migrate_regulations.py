import itertools
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
        self.model_classes = [
            Chapter,
            Heading,
            SubHeading,
            Commodity,
        ]
        self.m2m_map = {
            Chapter: "chapters",
            Heading: "headings",
            SubHeading: "subheadings",
            Commodity: "commodities",
        }

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

    def test_migrate_regulation_groups_between_commodity_objects(self):
        objects_to_assert = []

        for from_obj_class, to_obj_class in itertools.permutations(
            self.model_classes, 2
        ):
            from_obj = mixer.blend(from_obj_class, nomenclature_tree=self.tree)

            m2m_kwargs = {self.m2m_map[from_obj_class]: from_obj}
            regulation_group = mixer.blend(RegulationGroup, **m2m_kwargs)
            regulation_group.nomenclature_trees.add(self.tree)
            regulation_group.save()

            another_regulation_group = mixer.blend(RegulationGroup, **m2m_kwargs)
            another_regulation_group.nomenclature_trees.add(self.tree)
            another_regulation_group.save()

            to_obj = mixer.blend(
                to_obj_class,
                goods_nomenclature_sid=from_obj.goods_nomenclature_sid,
                nomenclature_tree=self.new_tree,
            )

            objects_to_assert.append(
                (
                    from_obj_class,
                    to_obj_class,
                    regulation_group,
                    another_regulation_group,
                    to_obj,
                )
            )

        call_command("migrate_regulations", stdout=sys.stdout)

        for (
            from_obj_class,
            to_obj_class,
            regulation_group,
            another_regulation_group,
            to_obj,
        ) in objects_to_assert:
            self.assertIn(regulation_group, to_obj.regulationgroup_set.all())
            self.assertIn(another_regulation_group, to_obj.regulationgroup_set.all())
            self.assertEqual(to_obj.regulationgroup_set.count(), 2)

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

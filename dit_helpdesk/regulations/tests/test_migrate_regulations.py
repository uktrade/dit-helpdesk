import sys
import logging

from mixer.backend.django import mixer

from django.core.management import call_command
from django.test import override_settings, TestCase
from django.utils import timezone

from hierarchy.models import Section, Chapter, Heading, SubHeading, NomenclatureTree
from commodities.models import Commodity
from regulations.models import RegulationGroup

from hierarchy.helpers import create_nomenclature_tree


logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


test_hierarchy_model_map = {
    "Commodity": {"file_name": "test_subsets/commodities.json", "app_name": "commodities"},
    "Chapter": {"file_name": "test_subsets/chapters.json", "app_name": "hierarchy"},
    "Heading": {"file_name": "test_subsets/headings.json", "app_name": "hierarchy"},
    "SubHeading": {"file_name": "test_subsets/sub_headings.json", "app_name": "hierarchy"},
    "Section": {"file_name": "test_subsets/sections.json", "app_name": "hierarchy"},
}


class MigrateRegulationsTest(TestCase):

    def setUp(self) -> None:
        self.tree = create_nomenclature_tree()
        self.section = mixer.blend(Section, nomenclature_tree=self.tree)
        self.chapter = mixer.blend(Chapter, section=self.section, nomenclature_tree=self.tree)
        self.heading = mixer.blend(Heading, chapter=self.chapter, nomenclature_tree=self.tree)
        self.subheading = mixer.blend(SubHeading, heading=self.heading, nomenclature_tree=self.tree)
        self.commodity = mixer.blend(
            Commodity, parent_subheading=self.subheading, nomenclature_tree=self.tree)

        self.new_tree = NomenclatureTree.objects.create(
            region="UK", start_date=timezone.now(), end_date=timezone.now())
        self.new_commodity = mixer.blend(
            Commodity,
            commodity_code=self.commodity.commodity_code,
            nomenclature_tree=self.new_tree
        )

    @override_settings(HIERARCHY_MODEL_MAP=test_hierarchy_model_map)
    def test_migrate_regulation_groups(self):
        regulation_group = mixer.blend(RegulationGroup, commodities=self.commodity)
        regulation_group.nomenclature_trees.add(self.tree)
        regulation_group.save()

        call_command('migrate_regulations', stdout=sys.stdout)

        self.assertIn(self.new_tree, regulation_group.nomenclature_trees.all())
        self.assertEqual(self.new_tree.regulationgroup_set.count(), 1)

    @override_settings(HIERARCHY_MODEL_MAP=test_hierarchy_model_map)
    def test_migrate_nomenclature_objects(self):
        regulation_group = mixer.blend(RegulationGroup, commodities=self.commodity)
        regulation_group.nomenclature_trees.add(self.tree)
        regulation_group.save()

        call_command('migrate_regulations', stdout=sys.stdout)

        self.assertIn(regulation_group, self.new_commodity.regulationgroup_set.all())
        self.assertEqual(self.new_commodity.regulationgroup_set.count(), 1)

import logging
import sys
from time import sleep

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from hierarchy.models import NomenclatureTree
from hierarchy.helpers import delete_all_inactive_trees, create_nomenclature_tree
from trade_tariff_service.HierarchyBuilder import HierarchyBuilder

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("section_id", type=int, nargs="?", default=None)
        parser.add_argument("--skip_commodity", action="store_true", default=False)
        parser.add_argument("--activate_new_tree", action="store_true", default=False)

    def handle(self, *args, **options):

        model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]

        with transaction.atomic():

            with transaction.atomic():
                prev_eu_tree = NomenclatureTree.get_active_tree('EU')
                # creating new tree automatically activates it (at least within transaction)
                new_eu_tree = create_nomenclature_tree('EU')

                builder = HierarchyBuilder(new_tree=new_eu_tree)
                builder.data_scanner(model_names)
                builder.process_orphaned_subheadings()
                builder.process_orphaned_commodities(options['skip_commodity'])

                if not options["activate_new_tree"]:
                    # switch back active tree to previous since we only want to properly activate
                    # the new one after we reindex ElasticSearch results
                    if prev_eu_tree:
                        prev_eu_tree.end_date = None
                        prev_eu_tree.save()

                    new_eu_tree.end_date = timezone.now()
                    new_eu_tree.save()

            with transaction.atomic():
                # we are not indexing UK documents in ElasticSearch (at least yet) so we can
                # safely activate this tree
                builder = HierarchyBuilder(region='UK')
                builder.data_scanner(model_names)
                builder.process_orphaned_subheadings()
                builder.process_orphaned_commodities(options['skip_commodity'])

import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from hierarchy.models import NomenclatureTree
from hierarchy.helpers import create_nomenclature_tree
from trade_tariff_service.HierarchyBuilder import HierarchyBuilder

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = """
        Process output files created from `pull_api_update` and `prepare_import_data` commands.
        Creates model instances and binds them to a new NomenclatureTree.
        The new NomenclatureTree is left inactive (so that it can be switched on after 
        ElasticSearch indexing is completed), unless specifically 
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip_commodity", action="store_true", default=False,
            help="Skip processing orphaned commodities"
        )
        parser.add_argument(
            "--activate_new_tree", action="store_true", default=False,
            help="Activate new NomenclatureTree with newly populated data right away. "
                 "May lead to inconsistent state if there is other data to be loaded/updated."
        )

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

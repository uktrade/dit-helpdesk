import logging
import sys
from time import sleep

from django.core.management.base import BaseCommand
from django.db import transaction

from hierarchy.models import Section
from hierarchy.helpers import delete_all_inactive_trees
from trade_tariff_service.HierarchyBuilder import HierarchyBuilder

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("section_id", type=int, nargs="?", default=None)
        parser.add_argument("--skip_commodity", action="store_true", default=False)
        parser.add_argument("--keep-old", action="store_true", default=False)

    def handle(self, *args, **options):

        model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]

        with transaction.atomic():

            with transaction.atomic():
                builder = HierarchyBuilder(region='EU')
                builder.data_scanner(model_names)
                builder.process_orphaned_subheadings()
                builder.process_orphaned_commodities(options['skip_commodity'])

            with transaction.atomic():
                builder = HierarchyBuilder(region='UK')
                builder.data_scanner(model_names)
                builder.process_orphaned_subheadings()
                builder.process_orphaned_commodities(options['skip_commodity'])

            if not options['keep_old']:
                delete_all_inactive_trees('EU')
                delete_all_inactive_trees('UK')

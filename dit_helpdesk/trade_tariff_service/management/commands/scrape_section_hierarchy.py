import logging
import sys
from time import sleep

from django.core.management.base import BaseCommand

from hierarchy.models import Section
from trade_tariff_service.HierarchyBuilder import HierarchyBuilder

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("section_id", type=int, nargs="?", default=None)
        parser.add_argument("--skip_commodity", type=bool, default=False)

    def handle(self, *args, **options):
        sections = Section.objects.all()
        if len(sections) > 0:
            logger.info("It looks like the hierarchy already exists.")
            return

        builder = HierarchyBuilder()
        model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]
        builder.data_scanner(model_names)
        builder.process_orphaned_subheadings()
        builder.process_orphaned_commodities(options['skip_commodity'])

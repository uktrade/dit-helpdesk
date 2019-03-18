import json
from time import sleep

from django.core.management.base import BaseCommand

from trade_tariff_service.importer import HierarchyBuilder


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('section_id', type=int, nargs='?', default=None)

    def handle(self, *args, **options):

        builder = HierarchyBuilder()
        model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]
        builder.data_scanner(model_names)
        sleep(60)
        builder.process_orphaned_subheadings()
        sleep(60)
        builder.process_orphaned_commodities()

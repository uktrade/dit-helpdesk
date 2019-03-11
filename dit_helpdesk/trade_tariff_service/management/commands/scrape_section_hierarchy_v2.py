import json

from django.core.management.base import BaseCommand

from trade_tariff_service.importer import HierarchyBuilder


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('section_id', type=int, nargs='?', default=None)

    def handle(self, *args, **options):

        builder = HierarchyBuilder()
        model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]
        builder.data_scanner(model_names)
        builder.process_orphaned_subheadings()
        builder.process_orphaned_commodities()

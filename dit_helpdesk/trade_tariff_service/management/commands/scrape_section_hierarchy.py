import sys
from time import sleep

from django.core.management.base import BaseCommand

from hierarchy.models import Section
from trade_tariff_service.HierarchyBuilder import HierarchyBuilder


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('section_id', type=int, nargs='?', default=None)

    def handle(self, *args, **options):

        sections = Section.objects.all()
        if len(sections) > 0:
            self.stdout.write("It looks like the hierarchy already exists.")
            return

        builder = HierarchyBuilder()
        model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]
        builder.data_scanner(model_names)
        builder.process_orphaned_subheadings()
        builder.process_orphaned_commodities()

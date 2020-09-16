from time import sleep

from django.core.management.base import BaseCommand

from trade_tariff_service.HierarchyBuilder import HierarchyBuilder


class Command(BaseCommand):
    def handle(self, *args, **options):

        # this just creates JSON files with data, which currently will be the same for EU and UK
        # once we get the data from different sources, we'll probably have to call different things
        # here for EU and UK
        builder = HierarchyBuilder()
        builder.build_import_data()

from time import sleep

from django.core.management.base import BaseCommand

from trade_tariff_service.HierarchyBuilder import HierarchyBuilder


class Command(BaseCommand):
    def handle(self, *args, **options):

        builder = HierarchyBuilder()
        # builder.get_chapter_data_from_api()
        # builder.get_tt_api_json()
        builder.build_import_data()

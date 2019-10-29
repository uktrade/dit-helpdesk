from time import sleep

from django.core.management.base import BaseCommand

from trade_tariff_service.HierarchyBuilder import HierarchyBuilder


class Command(BaseCommand):
    def handle(self, *args, **options):

        builder = HierarchyBuilder()
        builder.save_trade_tariff_service_api_data_json_to_file()

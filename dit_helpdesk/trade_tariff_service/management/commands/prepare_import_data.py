from django.conf import settings
from django.core.management.base import BaseCommand

from trade_tariff_service.HierarchyBuilder import HierarchyBuilder


class Command(BaseCommand):
    def handle(self, *args, **options):
        builder = HierarchyBuilder(region=settings.PRIMARY_REGION)
        builder.build_import_data()

        builder = HierarchyBuilder(region=settings.SECONDARY_REGION)
        builder.build_import_data()

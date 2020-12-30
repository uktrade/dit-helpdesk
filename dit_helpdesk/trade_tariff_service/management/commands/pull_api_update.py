import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from trade_tariff_service.HierarchyBuilder import HierarchyBuilder

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info(f"Pulling API data for {settings.PRIMARY_REGION}")
        builder = HierarchyBuilder(region=settings.PRIMARY_REGION)
        builder.save_trade_tariff_service_api_data_json_to_file()

        logger.info(f"Pulling API data for {settings.SECONDARY_REGION}")
        builder = HierarchyBuilder(region=settings.SECONDARY_REGION)
        builder.save_trade_tariff_service_api_data_json_to_file()

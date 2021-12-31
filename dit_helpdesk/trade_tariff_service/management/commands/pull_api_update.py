import logging

import concurrent.futures

from django.conf import settings
from django.core.management.base import BaseCommand

from trade_tariff_service.HierarchyBuilder import HierarchyBuilder

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


def pull_data(region):
    logger.info("Pulling API data for %s", region)
    builder = HierarchyBuilder(region)
    builder.save_trade_tariff_service_api_data_json_to_file()
    logger.info("Completed pull API data for %s", region)


class Command(BaseCommand):
    def handle(self, *args, **options):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for region in [settings.PRIMARY_REGION, settings.SECONDARY_REGION]:
                executor.submit(pull_data, region)

import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from trade_tariff_service.HierarchyBuilder import (
    HierarchyBuilder,
    MissingDescriptionsError,
    DuplicatedDescriptionsError,
)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        has_errors = False

        for region in [settings.PRIMARY_REGION, settings.SECONDARY_REGION]:
            builder = HierarchyBuilder(region=region)
            try:
                builder.build_import_data()
            except MissingDescriptionsError:
                logger.error("Found missing descriptions in %s", region)
            except DuplicatedDescriptionsError:
                logger.error("Found duplicated descriptions in %s", region)

        if has_errors:
            raise CommandError("Found errors when building import data")

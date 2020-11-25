from datetime import datetime
import logging

import dateutil.parser

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from django.utils import timezone

from hierarchy.models import NomenclatureTree
from hierarchy.helpers import create_nomenclature_tree
from trade_tariff_service.HierarchyBuilder import HierarchyBuilder

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = """
        Copies an existing active NomenclatureTree, but with a specific start date. It is expected
        that this will be changed to populate the database and Redis with different data

        Expected usage:
        python3 manage.py copy_section_hierarchy --region UK --start_date 2020-12-31T23:00 --region UK --start_date 2020-12-31T23:00Z
    """

    def add_arguments(self, parser):
        parser.add_argument("--region", nargs=1, required=True,
                            help="Region of source tree")
        parser.add_argument("--start_date", nargs=1, required=True, type=dateutil.parser.parse,
                            help="When the target tree starts")

    def handle(self, *args, **options):
        region = options['region'][0]
        start_date = options['start_date'][0]

        existing_tree = NomenclatureTree.get_active_tree(region)
        NomenclatureTree.objects.create(
            region=existing_tree.region,
            start_date=options['start_date'],
            end_date=None,
        )

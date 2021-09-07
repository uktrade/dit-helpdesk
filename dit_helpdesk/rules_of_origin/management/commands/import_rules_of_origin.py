#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from tempfile import NamedTemporaryFile

from django.conf import settings
from django.core.management.base import BaseCommand

from rules_of_origin.models import Rule, SubRule, RulesDocument, RulesDocumentFootnote
from rules_of_origin.ingest.importer import import_roo, check_countries_consistancy
from rules_of_origin.ingest.s3 import _get_s3_bucket

from hierarchy.models import NomenclatureTree
from hierarchy.helpers import process_swapped_tree


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--reset-all", action="store_true")

    def handle(self, *args, **options):
        with process_swapped_tree():
            self._handle(*args, **options)

    def _import_from_s3(self):
        bucket = _get_s3_bucket(
            bucket_name=settings.ROO_S3_BUCKET_NAME,
            access_key_id=settings.ROO_S3_ACCESS_KEY_ID,
            access_key=settings.ROO_S3_SECRET_ACCESS_KEY,
            endpoint_url=settings.S3_URL,
        )

        summaries = bucket.objects.filter(Prefix="rules_of_origin/")
        xml_objects = [s.Object() for s in summaries if s.key.endswith(".xml")]

        logger.info(
            "Retrieved %s XML files containing Rules of Origin data from s3 bucket",
            len(xml_objects),
        )
        if len(xml_objects) < 1:
            raise Exception("No Rules of Origin files in s3 Bucket")

        for obj in xml_objects:
            with NamedTemporaryFile(mode="w+b") as temp_file:
                self.stdout.write(f"Attempting to download object {obj.key} from S3")
                obj.download_fileobj(temp_file)
                self.stdout.write(f"Downloaded {obj.key}..")

                temp_file.flush()
                temp_file.seek(0)

                logger.info("Importing from S3 path %s", obj.key)
                import_roo(temp_file)

        check_countries_consistancy()

    def _handle(self, *args, **options):
        s3_bucket = settings.ROO_S3_BUCKET_NAME

        active_tree = NomenclatureTree.get_active_tree()
        logger.info("Importing rules of origin for %s", active_tree)

        if s3_bucket:
            logger.info("Deleting rules documents…")
            RulesDocument.objects.filter(nomenclature_tree=active_tree).all().delete()

            if options["reset_all"]:
                logger.info("Resetting all…")
                for cls in Rule, SubRule, RulesDocument, RulesDocumentFootnote:
                    logger.info("Deleting %s objects", cls)
                    cls.objects.all().delete()

            self._import_from_s3()
        else:
            self.stdout.write("S3 bucket for RoO files not provided, skipping.")

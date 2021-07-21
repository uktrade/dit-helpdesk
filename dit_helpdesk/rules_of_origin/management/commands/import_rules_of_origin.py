#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from tempfile import NamedTemporaryFile

from django.conf import settings
from django.core.management.base import BaseCommand

from rules_of_origin.models import Rule, SubRule, RulesDocument, RulesDocumentFootnote
from rules_of_origin.ingest.importer import import_roo
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

    def _import_local(self, path):
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                if len(files) <= 1:
                    # If the only file is the .gitkeep file, we have no data files and need to error
                    raise Exception(
                        f"There are no Rule Of Origin XML files stored at the given filepath: {path}"
                    )

                for filename in files:
                    if not filename.endswith(".xml"):
                        logger.info(
                            "Local import file "
                            + filename
                            + " is not an XML file, skipping to next file."
                        )
                        continue

                    full_path = os.path.join(root, filename)
                    logger.info("Importing from local path %s", full_path)
                    import_roo(full_path)

        else:
            logger.info("Importing from local path %s", path)
            import_roo(path)

    def _import_from_s3(self):
        bucket = _get_s3_bucket(
            bucket_name=settings.ROO_S3_BUCKET_NAME,
            access_key_id=settings.ROO_S3_ACCESS_KEY_ID,
            access_key=settings.ROO_S3_SECRET_ACCESS_KEY,
        )

        summaries = bucket.objects.filter(Prefix="rules_of_origin/")
        xml_objects = [s.Object() for s in summaries if s.key.endswith(".xml")]

        logger.info(
            f"Retrieved {len(xml_objects)} XML files containing Rules of Origin data from s3 bucket"
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

    def _handle(self, *args, **options):
        local_path = settings.RULES_OF_ORIGIN_DATA_PATH
        s3_bucket = settings.ROO_S3_BUCKET_NAME

        active_tree = NomenclatureTree.get_active_tree()
        logger.info("Importing rules of origin for %s", active_tree)

        if any([local_path, s3_bucket]):
            logger.info("Deleting rules documents…")
            RulesDocument.objects.filter(nomenclature_tree=active_tree).all().delete()

            if options["reset_all"]:
                logger.info("Resetting all…")
                for cls in Rule, SubRule, RulesDocument, RulesDocumentFootnote:
                    logger.info("Deleting %s objects", cls)
                    cls.objects.all().delete()

        if s3_bucket:
            logger.info("Importing from S3")
            self._import_from_s3()
        elif local_path:
            logger.info("Importing from local path")
            self._import_local(local_path)
        else:
            self.stdout.write(
                "Neither S3 credentials nor local path for RoO files provided, skipping."
            )

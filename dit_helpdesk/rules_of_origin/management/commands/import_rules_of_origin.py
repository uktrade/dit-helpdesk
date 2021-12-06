#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from tempfile import NamedTemporaryFile

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from rules_of_origin.models import Rule, SubRule, RulesDocument, RulesDocumentFootnote
from rules_of_origin.ingest.importer import (
    import_roo,
    check_countries_consistency,
    RulesDocumentAlreadyExistsException,
)
from rules_of_origin.ingest.postprocess import postprocess_rules_of_origin
from rules_of_origin.ingest.s3 import _get_s3_bucket


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            self._handle(*args, **options)

    def _find_duplicate(self, country, mapping):
        for obj_key, rule_document in mapping.items():
            if rule_document.countries.filter(pk=country.pk).exists():
                return obj_key

        return None

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

        rules_documents_mapping = {}
        for obj in xml_objects:
            with NamedTemporaryFile(mode="w+b") as temp_file:
                self.stdout.write(f"Attempting to download object {obj.key} from S3")
                obj.download_fileobj(temp_file)
                self.stdout.write(f"Downloaded {obj.key}..")

                temp_file.flush()
                temp_file.seek(0)

                logger.info("Importing from S3 path %s", obj.key)
                try:
                    rules_document = import_roo(temp_file)
                except RulesDocumentAlreadyExistsException as e:
                    duplicated_country = e.country
                    duplicated_obj_key = self._find_duplicate(
                        duplicated_country, rules_documents_mapping
                    )
                    logger.error(
                        "Failed to import %s. Found duplicate country %s. Already created from %s",
                        obj.key,
                        duplicated_country,
                        duplicated_obj_key,
                    )
                    raise e
                rules_documents_mapping[obj.key] = rules_document

        check_countries_consistency()

    def _handle(self, *args, **options):
        s3_bucket = settings.ROO_S3_BUCKET_NAME

        if s3_bucket:
            logger.info("Deleting rules documents…")
            RulesDocument.objects.all().delete()

            if options["reset_all"]:
                logger.info("Resetting all…")
                for cls in Rule, SubRule, RulesDocument, RulesDocumentFootnote:
                    logger.info("Deleting %s objects", cls)
                    cls.objects.all().delete()
            self._import_from_s3()
            postprocess_rules_of_origin()
        else:
            self.stdout.write("S3 bucket for RoO files not provided, skipping.")

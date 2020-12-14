#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.core.management.base import BaseCommand

from rules_of_origin.models import Rule, SubRule, RulesDocument, RulesDocumentFootnote
from rules_of_origin.ingest.importer import import_roo
from rules_of_origin.ingest.s3 import _get_s3_bucket

from hierarchy.helpers import process_swapped_tree


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true")

    def handle(self, *args, **options):
        with process_swapped_tree():
            self._handle(*args, **options)

    def _import_local(self, path):
        if os.path.isdir(path):

            for root, dirs, files in os.walk(path):
                for filename in files:
                    if not filename.endswith(".xml"):
                        continue

                    import_roo(os.path.join(root, filename))

        else:
            import_roo(path)

    def _import_from_s3(self):
        bucket = _get_s3_bucket(
            bucket_name=settings.ROO_S3_BUCKET_NAME,
            access_key_id=settings.ROO_S3_ACCESS_KEY_ID,
            access_key=settings.ROO_S3_SECRET_ACCESS_KEY,
        )

        summaries = bucket.objects.filter(Prefix='rules_of_origin/')
        xml_objects = [s.Object() for s in summaries if s.key.endswith('.xml')]

        for obj in xml_objects:
            with NamedTemporaryFile(mode='w+b') as temp_file:
                self.stdout.write(f"Attempting to download object {obj.key} from S3")
                obj.download_fileobj(temp_file)
                self.stdout.write(f"Downloaded {obj.key}..")

                temp_file.flush()
                temp_file.seek(0)

                import_roo(temp_file)

    def _handle(self, *args, **options):

        local_path = settings.RULES_OF_ORIGIN_DATA_PATH
        s3_bucket = settings.ROO_S3_BUCKET_NAME

        if any([local_path, s3_bucket]) and options["reset"]:
            for cls in Rule, SubRule, RulesDocument, RulesDocumentFootnote:
                cls.objects.all().delete()

        if s3_bucket:
            self._import_from_s3()
        elif local_path:
            self._import_local(local_path)
        else:
            self.stdout.write(
                "Neither S3 credentials nor local path for RoO files provided, skipping.")

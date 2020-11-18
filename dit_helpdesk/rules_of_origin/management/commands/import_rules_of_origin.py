#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from rules_of_origin.models import Rule, RulesDocument, RulesDocumentFootnote
from rules_of_origin.ingest.importer import import_roo

from hierarchy.helpers import process_swapped_tree


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true")

    def handle(self, *args, **options):
        with process_swapped_tree():
            self._handle(*args, **options)

    def _handle(self, *args, **options):

        path = settings.RULES_OF_ORIGIN_DATA_PATH

        if options["reset"]:
            for cls in Rule, RulesDocument, RulesDocumentFootnote:
                cls.objects.all().delete()

        if os.path.isdir(path):

            for root, dirs, files in os.walk(path):
                for filename in files:
                    if not filename.endswith(".xml"):
                        continue

                    import_roo(os.path.join(root, filename))

        else:
            import_roo(path)

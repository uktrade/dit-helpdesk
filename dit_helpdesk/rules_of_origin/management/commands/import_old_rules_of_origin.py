#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from rules_of_origin.models import OldRule, OldRulesDocument, OldRulesDocumentFootnote, OldRulesGroup, OldRulesGroupMember
from rules_of_origin.RulesOfOriginImporter import RulesOfOriginImporter

from hierarchy.models import NomenclatureTree
from hierarchy.helpers import process_swapped_tree


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--data_path", type=str, nargs="?", required=True)
        parser.add_argument("--output_file", default=None)
        parser.add_argument("--priority", type=int, nargs="?", default=1)
        parser.add_argument("--reset", action="store_true")

    def handle(self, *args, **options):
        with process_swapped_tree():
            self._handle(*args, **options)

    def _handle(self, *args, **options):

        if options["data_path"] is None:
            raise CommandError(
                "\nNo value has been provided for the argument --data_path.\n\n"
            )

        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(options["data_path"])

        if os.path.isfile(path) and not path.endswith(".json"):
            raise CommandError(
                "\nThis command only works with .json files.\n\n".format()
            )

        if not os.path.exists(path):
            raise CommandError(
                "\nThe file path below does not exist."
                "\n\n\t{0}\n"
                "\nPlease provide a correct path relative to that shown below and run the command again"
                "\n\n\t{1}\n\n".format(path, settings.OLD_RULES_OF_ORIGIN_DATA_PATH[:-3])
            )

        with transaction.atomic():
            if options["reset"]:
                for cls in OldRule, OldRulesDocument, OldRulesDocumentFootnote, OldRulesGroup, OldRulesGroupMember:
                    cls.objects.all().delete()

            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    if not all(
                        [
                            True if file.endswith(".json") else False
                            for file in files
                            if not file.endswith(".csv") and not file.startswith(".")
                        ]
                    ):
                        raise CommandError(
                            "\nThis command only works with .json and .csv files."
                            "\nPlease remove any non .json or .csv files from the following location"
                            "and run the command again\n\n\t{0}\n\n".format(path)
                        )
                    for filename in files:

                        if not filename.endswith(".csv") and not filename.startswith(
                            "."
                        ):
                            importer = RulesOfOriginImporter()
                            imported = importer.load(
                                input_file=os.path.join(path, filename),
                                output_file=os.path.join(
                                    path, filename.replace(".json", ".out.json")
                                ),
                                priority=options["priority"],
                            )
                            if imported:
                                importer.instance_builder()

            else:
                importer = RulesOfOriginImporter()
                imported = importer.load(
                    input_file=path,
                    output_file=path.replace(".json", ".out.json"),
                    priority=options["priority"],
                )
                if imported:
                    importer.instance_builder()
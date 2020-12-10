#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from rules_of_origin.DocxScraper import DocxScraper


class Command(BaseCommand):
    requires_migrations_checks = True
    requires_system_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
            "--docx_path",
            nargs="?",
            required=True,
            type=str,
            help="Provides a file system location for the command to read files from",
        )

    def handle(self, *args, **options):

        if options["docx_path"] is None:
            raise CommandError(
                "\nNo value has been provided for the argument --docx_path.\n\n"
            )

        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(options["docx_path"])

        if os.path.isfile(path) and not path.endswith(".docx"):
            raise CommandError(
                "\nThis command only works with MS Word .docx files.\n\n".format()
            )

        if not os.path.exists(path):
            raise CommandError(
                "\nThe file path below does not exist."
                "\n\n\t{0}\n"
                "\nPlease provide a correct path relative to that shown below and run the command again"
                "\n\n\t{1}\n\n".format(path, settings.OLD_RULES_OF_ORIGIN_DATA_PATH[:-3])
            )

        else:
            scraper = DocxScraper()
            if os.path.isdir(path):

                for root, dirs, files in os.walk(path):
                    if not all(
                        [
                            True if file.endswith(".docx") else False
                            for file in files
                            if not file.startswith("~$") and not file.startswith(".")
                        ]
                    ):
                        raise CommandError(
                            "\nThis command only works with MS Word .docx files."
                            "\nPlease remove any non .docx files from the following location"
                            "and run the command again\n\n\t{}\n\n".format(path)
                        )
                    for filename in files:

                        if not filename.startswith("~$") and not filename.startswith(
                            "."
                        ):
                            scraper.load(
                                docx_file=os.path.join(options["docx_path"], filename)
                            )

            else:
                scraper.load(docx_file=options["docx_path"])

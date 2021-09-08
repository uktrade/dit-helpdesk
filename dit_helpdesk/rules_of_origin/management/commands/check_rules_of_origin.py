#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from rules_of_origin.ingest.importer import check_countries_consistency

from hierarchy.helpers import process_swapped_tree


class Command(BaseCommand):
    def handle(self, *args, **options):
        with process_swapped_tree():
            self.stdout.write(
                "Checking rules of origin - Checking if we currently have "
                "Rules Documents for all countries we expect."
            )
            check_countries_consistency()

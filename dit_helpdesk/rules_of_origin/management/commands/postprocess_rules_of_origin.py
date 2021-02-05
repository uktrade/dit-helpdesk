#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from rules_of_origin.ingest.postprocess import postprocess_rules_of_origin

from hierarchy.helpers import process_swapped_tree


class Command(BaseCommand):

    def handle(self, *args, **options):
        with process_swapped_tree():
            self.stdout.write(
                "Post-processing rules of origin - forrmatting HS codes and abbreviations..")
            postprocess_rules_of_origin()

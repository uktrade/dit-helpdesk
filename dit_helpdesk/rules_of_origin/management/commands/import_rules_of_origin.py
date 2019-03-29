#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from collections import defaultdict
import json
import re
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from rules_of_origin.importer import RulesOfOriginImporter


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--data_file', default=None)

    def handle(self, *args, **options):
        print("importer : ", options['data_file'])
        if options['data_file'] is None:
            sys.exit()
        importer = RulesOfOriginImporter()
        importer.load(data_file=options['data_file'])

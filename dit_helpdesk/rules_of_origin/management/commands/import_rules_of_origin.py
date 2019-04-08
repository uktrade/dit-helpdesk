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
        parser.add_argument('--input_file', default=None)
        parser.add_argument('--output_file', default=None)
        parser.add_argument('--documents_file', default=None)
        parser.add_argument('--groups_file', default=None)
        parser.add_argument('--priority', type=int, nargs='?', default=1)

    def handle(self, *args, **options):
        opts = {option: options[option] for option in options if option.endswith('_file')}
        print(opts)
        print({'priority': options['priority']})
        if None in opts.values():
            print ("{0} is missing".format(list(opts.keys())[list(opts.values()).index(None)]))
            sys.exit()
        importer = RulesOfOriginImporter()
        importer.load(input_file=options['input_file'],
                      output_file=options['output_file'],
                      documents_file=options['documents_file'],
                      groups_file=options['groups_file'],
                      priority=options['priority'])

#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from flags.models import FlagState


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--list", action="store_true")
        parser.add_argument("--set_bool", action="store_true")

    def handle(self, *args, **options):
        pass

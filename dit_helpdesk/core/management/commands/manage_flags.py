#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from flags.models import FlagState


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("-l", "--list", action="store_true", help="List flags")
        parser.add_argument(
            "-s", "--set", nargs="*", action="store",
            help="Set a flag value. Usage: --set flag_name flag_value")

    def list_flags(self):
        flags = FlagState.objects.order_by('name').all()

        for flag in flags:
            self.stdout.write(
                f"Name: {flag.name}\t Condition: {flag.condition}\t Value: {flag.value}")

    def set_flag(self, name, value):
        flag = FlagState.objects.get(
            name=name)

        flag.value = value
        flag.save()

    def handle(self, *args, **options):
        if options["list"]:
            self.list_flags()
        elif options["set"]:
            try:
                name, value = options["set"]
            except ValueError as e:
                raise CommandError("Provide 2 values for the set option") from e

            self.set_flag(name, value)

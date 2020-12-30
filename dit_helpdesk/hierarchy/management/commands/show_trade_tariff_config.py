import pprint

from django.core.management.base import BaseCommand

from ...clients import get_settings_config


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(
            pprint.pformat(get_settings_config()),
        )

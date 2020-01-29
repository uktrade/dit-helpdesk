import os

from django.conf import settings
from django.core.management.base import BaseCommand
from shutil import copy

STATIC_TEST_FIXTURES = settings.IMPORT_DATA_PATH.format('test_prepared')
DATA_SOURCE = settings.IMPORT_DATA_PATH.format('prepared')

class Command(BaseCommand):
    def handle(self, *args, **options):
        files = os.listdir(STATIC_TEST_FIXTURES)
        for f in files:
            copy("{dir_name}/{file_name}".format(dir_name=STATIC_TEST_FIXTURES, file_name=f), DATA_SOURCE)

import os

from django.conf import settings
from django.core.management.base import BaseCommand
from shutil import copy
from ...utils import createDir

STATIC_TEST_FIXTURES = settings.IMPORT_DATA_PATH.format("test")
DATA_SOURCE = settings.IMPORT_DATA_PATH.format("downloaded")


class Command(BaseCommand):
    def handle(self, *args, **options):
        createDir(DATA_SOURCE)
        files = os.listdir(STATIC_TEST_FIXTURES)
        for f in files:
            copy(
                "{dir_name}/{file_name}".format(
                    dir_name=STATIC_TEST_FIXTURES, file_name=f
                ),
                DATA_SOURCE,
            )

from django.conf import settings
from django.core.management.base import BaseCommand

from regulations.importer import RegulationsImporter


class Command(BaseCommand):
    help = """Command to import links to documents and regulations related to commodties"""

    def handle(self, *args, **options):

        data_path = settings.REGULATIONS_DATA_PATH

        importer = RegulationsImporter()
        importer.load(data_path)
        importer.process()

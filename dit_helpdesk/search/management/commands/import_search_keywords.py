from django.conf import settings
from django.core.management.base import BaseCommand
from search.importer import SearchKeywordsImporter


class Command(BaseCommand):
    # help = """Command to import links to documents and regulations related to commodties"""

    def add_arguments(self, parser):
        parser.add_argument('-f', '--data_path', type=str, nargs='?', required=True)

    def handle(self, *args, **options):

        importer = SearchKeywordsImporter()
        importer.load(options["data_path"])
        importer.process()

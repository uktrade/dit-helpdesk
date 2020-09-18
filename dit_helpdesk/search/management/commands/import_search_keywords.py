from django.core.management.base import BaseCommand
from search.importer import SearchKeywordsImporter

from hierarchy.helpers import process_swapped_tree


class Command(BaseCommand):
    # help = """Command to import links to documents and regulations related to commodties"""

    def add_arguments(self, parser):
        parser.add_argument("-f", "--data_path", type=str, nargs="?", required=True)

    def handle(self, *args, **options):

        with process_swapped_tree():
            importer = SearchKeywordsImporter()
            importer.load(options["data_path"])
            importer.process()

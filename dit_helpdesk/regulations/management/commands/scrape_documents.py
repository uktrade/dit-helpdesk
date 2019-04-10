import json
from time import sleep

from django.conf import settings
from django.core.management.base import BaseCommand

from regulations.documents_scraper import DocumentsScraper


class Command(BaseCommand):
    # help = """Command to import links to documents and regulations related to commodties"""

    def add_arguments(self, parser):
        parser.add_argument('-t', '--test-run', action='store_true', help='perform a test run without saving')

    def handle(self, *args, **options):

        scraper = DocumentsScraper()
        scraper.load()

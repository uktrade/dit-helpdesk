from django.conf import settings
from django.core.management.base import BaseCommand

from search.search_keyword_generator import SearchKeywordGenerator

HEADINGS_CSV = settings.SEARCH_DATA_PATH.format("commodities/hierarchy_subheading_all.csv")
GA_SEARCH_TERMS = settings.SEARCH_DATA_PATH.format(
    "google_analytics/Analytics All Web Site Data Search Terms 20180513-20190513.xlsx")
OUTPUT_FILE = settings.SEARCH_DATA_PATH.format('output/keywords_and_synonyms_merged.csv')
GREEN_PAGES_LIST = settings.SEARCH_DATA_PATH.format('synonyms/green_page_list.xlsx')


class Command(BaseCommand):
    # help = """Command to import links to documents and regulations related to commodties"""

    def add_arguments(self, parser):
        parser.add_argument('-f', '--data_path', type=str, nargs='?', required=False)

    def handle(self, *args, **options):
        generator = SearchKeywordGenerator(HEADINGS_CSV, GA_SEARCH_TERMS, GREEN_PAGES_LIST, OUTPUT_FILE)
        generator.process()

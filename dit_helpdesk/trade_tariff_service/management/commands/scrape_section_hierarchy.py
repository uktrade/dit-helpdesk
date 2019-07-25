import sys
from time import sleep

from django.core.management.base import BaseCommand

from hierarchy.models import Section
from trade_tariff_service.HierarchyBuilder import HierarchyBuilder
from trade_tariff_service.util_scraper import scrape_heading_hierarchy

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)

SECTION_URL = 'https://www.trade-tariff.service.gov.uk/trade-tariff/sections/%s.json'


def get_and_update_section(section_id):
    section_id = int(section_id)
    section_db_obj, _ = Section.objects.get_or_create(section_id=section_id)

    url = SECTION_URL % section_id
    resp = requests.get(url)
    resp_content = resp.content.decode()
    if resp.status_code != 200:
        exit('section gave 404')

    section_json_obj = SectionJson(json.loads(resp_content))

    section_db_obj.tts_json = resp_content  # json.dumps(section_json_obj.di)
    section_db_obj.save()

    return section_json_obj, section_db_obj


def get_and_update_chapter(chapter_url, section_db_obj):
    resp = requests.get(chapter_url)
    resp_content = resp.content.decode()
    if resp.status_code != 200:
        logger.debug('url failed: ' + chapter_url)
        return None, None

    chapter_json_obj = ChapterJson(json.loads(resp_content))
    chapter_db_obj, created = Chapter.objects.get_or_create(
        chapter_code=chapter_json_obj.harmonized_code
    )
    if created:
        chapter_db_obj.section = section_db_obj
    elif chapter_db_obj.section and chapter_db_obj.section != section_db_obj:
        logger.debug('multiple parent sections?')

    chapter_db_obj.tts_json = resp_content  # json.dumps(chapter_json_obj.di)
    chapter_db_obj.save()

    return chapter_json_obj, chapter_db_obj


def get_and_update_heading(heading_url, chapter_db_obj):

    resp = requests.get(heading_url)
    resp_content = resp.content.decode()
    if resp.status_code != 200:
        logger.debug('url failed: ' + heading_url)
        return None, None

    heading_json_obj = HeadingJson(json.loads(resp_content))
    heading_db_obj, created = Heading.objects.get_or_create(
        heading_code=heading_json_obj.code
    )

    if created:
        heading_db_obj.chapter = chapter_db_obj
    elif heading_db_obj.chapter and heading_db_obj.chapter != chapter_db_obj:
        logger.debug('multiple parent chapters?')

    heading_db_obj.tts_json = resp_content  # json.dumps(heading_json_obj.di)
    heading_db_obj.save()

    return heading_json_obj, heading_db_obj

import sys
from time import sleep

from django.core.management.base import BaseCommand

from hierarchy.models import Section
from trade_tariff_service.HierarchyBuilder import HierarchyBuilder

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('section_id', type=int, nargs='?', default=None)

    def handle(self, *args, **options):

        sections = Section.objects.all()
        if len(sections) > 0:
            self.stdout.write("It looks like the hierarchy already exists.")
            return

        builder = HierarchyBuilder()
        model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]
        builder.data_scanner(model_names)
        builder.process_orphaned_subheadings()
        builder.process_orphaned_commodities()

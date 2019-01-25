import json

from django.core.management.base import BaseCommand, CommandError
import requests

from requirements_documents.models import Commodity, Section, Chapter, Heading
from requirements_documents.tts_api import SectionJson, ChapterJson, HeadingJson, CommodityJson


SECTION_URL = 'https://www.trade-tariff.service.gov.uk/trade-tariff/sections/%s.json'


def get_and_update_section(section_id):
    section_db_obj, _ = Section.objects.get_or_create(section_id=section_id)

    url = SECTION_URL % section_id
    resp = requests.get(url)
    resp_content = resp.content.decode()
    if resp.status_code != 200:
        exit('section gave 404')

    section_json_obj = SectionJson(json.loads(resp_content))

    section_db_obj.tts_json = section_json_obj.di
    section_db_obj.save()

    return section_json_obj, section_db_obj


def get_and_update_chapter(chapter_url, section_db_obj):
    resp = requests.get(chapter_url)
    resp_content = resp.content.decode()
    if resp.status_code != 200:
        print('url failed: ' + chapter_url)
        return None, None

    chapter_json_obj = ChapterJson(json.loads(resp_content))
    chapter_db_obj, created = Chapter.objects.get_or_create(
        chapter_code=chapter_json_obj.code
    )
    if created:
        chapter_db_obj.section = section_db_obj
    elif chapter_db_obj.section and chapter_db_obj.section != section_db_obj:
        import pdb; pdb.set_trace()  # multiple parent sections?

    chapter_db_obj.tts_json = chapter_json_obj.di
    chapter_db_obj.save()

    return chapter_json_obj, chapter_db_obj


def get_and_update_heading(heading_url, chapter_db_obj):

    resp = requests.get(heading_url)
    resp_content = resp.content.decode()
    if resp.status_code != 200:
        print('url failed: ' + heading_url)
        return None, None

    heading_json_obj = HeadingJson(json.loads(resp_content))
    heading_db_obj, created = Heading.objects.get_or_create(
        heading_code=heading_json_obj.code
    )
    if created:
        heading_db_obj.chapter = chapter_db_obj
    elif heading_db_obj.chapter and heading_db_obj.chapter != chapter_db_obj:
        import pdb; pdb.set_trace()  # multiple parent chapters?
    heading_db_obj.tts_json = heading_json_obj.di
    heading_db_obj.save()

    return heading_json_obj, heading_db_obj


def get_and_update_commodity(commodity_url, is_leaf, heading_db_obj):
    resp = requests.get(commodity_url)
    resp_content = resp.content.decode()
    if resp.status_code != 200:
        print('url failed: ' + commodity_url)
        return None, None
    commodity_json_obj = CommodityJson(json.loads(resp_content))
    commodity_db_obj, created = Commodity.objects.get_or_create(
        commodity_code=commodity_json_obj.code
    )
    if created:
        commodity_db_obj.heading = heading_db_obj
    elif commodity_db_obj.heading and commodity_db_obj.heading != heading_db_obj:
        import pdb; pdb.set_trace()
    commodity_db_obj.tts_is_leaf = is_leaf
    commodity_db_obj.tts_json = commodity_json_obj.di
    commodity_db_obj.save()
    return commodity_db_obj


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('section_id', type=int, nargs='?', default=None)

    def handle(self, *args, **options):

        section_id = options['section_id']
        if section_id is None:
            exit('<section_id> argument expected')

        section_json_obj, section_db_obj = get_and_update_section(section_id)

        if section_json_obj is None:
            exit('Failed to query for section %s' % section_id)

        for chapter_url in section_json_obj.chapter_urls:
            print('----------------------------------------------')
            print('CHAPTER '+chapter_url)

            chapter_json_obj, chapter_db_obj = get_and_update_chapter(
                chapter_url, section_db_obj
            )
            if chapter_json_obj is None:
                continue

            for heading_url in chapter_json_obj.heading_urls:
                print('    HEADING '+heading_url)

                heading_json_obj, heading_db_obj = get_and_update_heading(
                    heading_url, chapter_db_obj
                )
                if heading_json_obj is None:
                    continue

                # for commodity_url, is_leaf in heading_json_obj.commodity_urls:
                #     print('        COMMODITY '+commodity_url)
                #     get_and_update_commodity(commodity_url, is_leaf, heading_db_obj)

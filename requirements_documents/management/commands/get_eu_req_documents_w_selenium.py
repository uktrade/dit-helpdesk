import json
from multiprocessing.pool import ThreadPool
import time
import re

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from psqlextra.query import ConflictAction
import requests
from collections import OrderedDict

from requirements_documents.models import Section, Commodity, RequirementDocument, HasRequirementDocument
from requirements_documents.util import mclean, fhtml
from requirements_documents.models import EuTradeHelpdeskDocument
from selenium.webdriver import Firefox
from random import shuffle


NETWORK_INFO_JS = 'var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;'

TAG_NAME_REGEX = re.compile('^<[/]?(.*?)[/]?>.*', flags=re.MULTILINE | re.DOTALL)

TAB_NUMS = OrderedDict([
    ('product_requirements', 2),
    ('import_procedures', 3),  # url tab numbers

])
TAB_TITLES = {
    "product_requirements": 'Product requirements',
    'import_procedures': 'Import Procedures',
}


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('section_id', type=int, nargs='?', default=None)

    def handle(self, *args, **options):

        section_id = options['section_id']
        if section_id is None:
            exit('<section_id> argument expected')

        get_documents_for_section(section_id)


def get_section_commodities(section_id):

    commodities = []
    section = Section.objects.get(section_id=section_id)
    for chapter in section.chapter_set.all():
        for heading in chapter.heading_set.all():
            for commodity in heading.commodity_set.all():
                commodities.append(commodity)
    return commodities


def get_documents_for_section(section_id):

    commodities = get_section_commodities(section_id)
    driver = Firefox()
    driver.set_window_size(1300, 2700)

    shuffle(commodities)  # todo: temporary

    for c_obj in commodities:
        code = c_obj.commodity_code

        for origin_country in settings.TTS_COUNTRIES:
            for tab_name in TAB_NUMS.keys():
                documents = get_documents_for_commodity(
                    driver, code, origin_country, tab_name
                )
                print('\nDocuments for %s %s %s:' % (code, origin_country, tab_name))
                for doc in documents:
                    print('    -' + doc['title'])
                print()

                save_documents(c_obj, origin_country, tab_name, documents)

        driver.quit()  # in case network_info is getting too large
        driver = Firefox()
        driver.set_window_size(1300, 2700)


def save_documents(comoodity_obj, origin_country, tab_name, document_dicts):
    for di in document_dicts:
        kwargs = {
            'title': di['title'], 'group_name': tab_name,
            'query_urls': di['query_urls'],
            'selenium_elem_html': di.get('selenium_elem_html'),
            'origin_country': origin_country, 'commodity': comoodity_obj
        }
        EuTradeHelpdeskDocument.objects.create(**kwargs)


def get_inner(outer_html):
    if outer_html is None:
        return None
    if outer_html.startswith('<') and outer_html.endswith('>') and outer_html.count('<') == 1 and outer_html.count('>') == 1:
        inner_html = ''
    else:
        try:
            tag_name = re.findall(TAG_NAME_REGEX, outer_html)[0].split(' ', 1)[0].lower()
        except:
            import pdb; pdb.set_trace()
        end_tag = '</' + tag_name + '>'
        if outer_html.startswith('<') and outer_html.endswith(end_tag):
            inner_html = outer_html[outer_html.index('>')+1:outer_html.rindex(end_tag)]
        else:
            inner_html = ''
    return inner_html.strip()


def get_text(elem):
    txt = elem.text.strip()
    if txt:
        return txt
    inner = get_inner(elem.get_attribute('outerHTML'))
    if '<' in inner:
        return ''  # or we could string out tags
    return inner


EXPORT_HEADER_XP = "//h1[contains(@class, 'page-header')]"


def get_documents_for_commodity(driver, commodity_code, origin_country, tab_name):
    url = 'http://trade.ec.europa.eu/tradehelp/myexport#?product=%s&partner=%s&reporter=GB' % (
        commodity_code, origin_country
    )
    driver.get(url)

    time.sleep(0.4)
    driver.execute_script("window.scrollBy(0,310)")
    time.sleep(0.1)

    tab_xp = "//ul[contains(@class, 'nav-tabs')]"
    tab_elems = driver.find_elements_by_xpath(tab_xp)[0].find_elements_by_xpath("./li")
    tab_elems = {e.text.strip(): e for e in tab_elems}
    target_tab = tab_elems[TAB_TITLES[tab_name]]
    time.sleep(0.55)
    #driver.execute_script("arguments[0].click();", target_tab)
    try:
        target_tab.click()
    except:
        for i in range(3):
            if i == 0:
                my_export_header = driver.find_elements_by_xpath(
                    EXPORT_HEADER_XP
                )
                if my_export_header:
                    try:
                        my_export_header[0].click()
                    except:
                        pass
                time.sleep(0.25)
                driver.execute_script("arguments[0].click();", target_tab)
                continue
            time.sleep(0.75)
            try:
                target_tab.click()  # todo: maybe try scrolling to it
            except:
                pass
        ans = input('correct tab selected? expecting: %s (y/n)' % tab_name).strip().upper()
        if ans == 'N':
            import pdb; pdb.set_trace()
    import pdb; pdb.set_trace()
    elems = [
        e for e in driver.find_elements_by_xpath('//a[@ng-click]')
        if 'openRequirementWindow' in e.get_attribute('outerHTML') or 'openEUOverviewWindow()' in e.get_attribute('outerHTML')
    ]
    elems = [e for e in elems if e.text.strip()]
    network_info = driver.execute_script(NETWORK_INFO_JS)
    documents = []
    for e in elems:
        try:
            driver.execute_script("arguments[0].click();", e)
            time.sleep(0.35)
        except:
            print('failed to click: ' + e.text)
            continue

        new_network_info = driver.execute_script(NETWORK_INFO_JS)[len(network_info):]
        query_urls = [
            di['name'] for di in new_network_info if '/requirement' in di['name']
        ]
        txt = get_text(e)
        if len(query_urls) not in (1,2):
            print('\nwarning: query_urls length: %s' % len(query_urls))
            print('details:          %s %s %s %s' % (
                commodity_code, tab_name, txt, origin_country
            ))

        documents.append({
            'title': txt, 'query_urls': query_urls, 'group_name': tab_name,
            'selenium_elem_html': e.get_attribute('outerHTML')
        })  # maybe also take a screenshot of the tab so we can verify by mechanical turk or OCR?
        network_info.extend(new_network_info)

        close_buttons = driver.find_elements_by_xpath("//div[contains(@class, 'ngdialog-close')]")
        for cb in close_buttons:
            try:
                driver.execute_script("arguments[0].click();", cb)
                time.sleep(0.5)
            except:
                try:
                    cb.click()
                except:
                    pass
                continue

        driver.execute_script("arguments[0].click();", target_tab)

    if tab_name == 'import_procedures':
        custom_clearance_links = driver.find_elements_by_xpath("//a[contains(text(), 'Documents for customs clearance')]")
        custom_clearance_urls = set([
            e.get_attribute('href') for e in custom_clearance_links
        ])
        custom_clearance_urls = [v for v in custom_clearance_urls]
        if custom_clearance_links and len(custom_clearance_urls) != 1:
            import pdb; pdb.set_trace()
            print()

        documents.append({
            'title': 'Documents for customs clearance',
            'query_urls': [custom_clearance_urls[0]],
            'group_name': tab_name,
            #  NOTE: this may be the wrong elem if number of urls > 1
            'selenium_elem_html': custom_clearance_links[0].get_attribute('outerHTML')
        })

    driver.execute_script("arguments[0].click();", target_tab)
    time.sleep(0.1)
    return documents

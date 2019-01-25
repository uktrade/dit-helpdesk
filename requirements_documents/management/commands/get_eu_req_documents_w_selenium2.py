import time
import re

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from requirements_documents.models import Section, Commodity, RequirementDocument, HasRequirementDocument
from requirements_documents.models import EuTradeHelpdeskDocument, EuTradeHelpdeskDocumentTitle, CommodityHasDocTitle
from selenium.webdriver import Firefox
from random import shuffle


NETWORK_INFO_JS = 'var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;'

TAG_NAME_REGEX = re.compile('^<[/]?(.*?)[/]?>.*', flags=re.MULTILINE | re.DOTALL)


#TTS_COUNTRIES = settings.TTS_COUNTRIES[:1]
TTS_COUNTRIES = [
    "AF", "CH", "BZ", "KP", "CN"
]


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


APPROVE_MANUALLY = True


def get_documents_for_section(section_id):

    commodities = get_section_commodities(section_id)
    import pdb; pdb.set_trace()
    driver = Firefox()
    driver.set_window_size(1300, 2700)

    #shuffle(commodities)  # todo: temporary

    for c_obj in commodities:
        code = c_obj.commodity_code
        for origin_country in TTS_COUNTRIES:
            document_titles = get_document_titles_for_commodity(
                driver, code, origin_country
            )

            if APPROVE_MANUALLY and document_titles:
                print('\n %s :' % code)
                print('\n'.join(document_titles))
                print()
                import pdb; pdb.set_trace()

            save_document_titles(c_obj, origin_country, document_titles)
    driver.quit()


def save_document_titles(commodity_obj, origin_country, document_titles):
    if not document_titles:
        return
    for title in document_titles:
        title_obj, _ = EuTradeHelpdeskDocumentTitle.objects.get_or_create(title=title)
        CommodityHasDocTitle.objects.get_or_create(
            commodity=commodity_obj, document_title=title_obj,
            origin_country=origin_country
        )


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
    if not txt:
        inner = get_inner(elem.get_attribute('outerHTML'))
        if '<' in inner:
            return ''  # or we could string out tags
        txt = inner

    txt = txt.replace('\n', ' ').replace('  ', ' ')
    return txt


EXPORT_HEADER_XP = "//h1[contains(@class, 'page-header')]"


def click_tab(driver, target_tab):
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
        ans = input('correct tab selected? (y/n)').strip().upper()
        if ans == 'N':
            import pdb; pdb.set_trace()


def get_document_titles_for_commodity(driver, commodity_code, origin_country):
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
    target_tab = tab_elems['Product requirements']
    time.sleep(0.55)
    click_tab(driver, target_tab)

    main_div = driver.find_elements_by_xpath("//div[contains(@id, 'myexportresults')]")[0]
    list_items = [
        e for e in main_div.find_elements_by_xpath('.//li') if get_text(e)
    ]

    return [
        get_text(e) for e in list_items
    ]

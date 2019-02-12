#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
from django.core.management.base import BaseCommand, CommandError
import requests
from bs4 import BeautifulSoup
import re
from collections import defaultdict
from hierarchy.models import Section, Chapter
from headings.models import Heading
from trade_tariff_service.tts_api import SectionJson, ChapterJson, HeadingJson
from trade_tariff_service.util_scraper import scrape_heading_hierarchy


RULES = defaultdict(list)
EXCLUSION_RULES = defaultdict(list)

roo_fp = '/Users/rossrochford/code/DIT/dit-helpdesk/dit_helpdesk/core/management/commands/roo.html'

'''

<tr class="table">
     <td valign="top" class="table">
        <p class="tbl-cod">1301</p>
     </td>
     <td valign="top" class="table">
        <p class="tbl-txt">Lac; natural gums, resins, gum-resins and oleoresins (for example, balsams)</p>
     </td>
     <td valign="top" class="table">
        <p class="tbl-cod">Manufacture in which the value of all the materials of heading 1301 used does not exceed 50&nbsp;% of the ex-works price of the product</p>
     </td>
     <td valign="top" class="table">
        <p class="normal">&nbsp;</p>
     </td>
</tr>
'''

# https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=uriserv:OJ.L_.2013.054.01.0003.01.ENG

'''

Chapter 1

0403

1507 to 1515
3003 and 3004
4107, 4112 and 4113
7304, 7305 and 7306

ex Chapter 4
ex ex0502

ex ex7616
ex ex2004 and ex ex2005
ex ex9601 and ex ex9602
ex ex4410 to ex ex4413
ex ex6202, ex ex6204, ex ex6206, ex ex6209 and ex ex6211


what do these mean? 
5004 to ex ex5006
ex ex7218, 7219 to 7222
ex ex7224, 7225 to 7228
8403 and ex ex8404

'''

st = 'ex ex9601 and ex ex9602'
st = st.replace(' and ', ', ')
st = st.replace(' to ', '-')

ROW_CATEGORY_REGEXPS = [

    (r'^ex Chapter (?P<chapter_num>\d{1,2})$', 'chapter_exclusion'),  # ex Chapter 4
    (r'^(ex ex\d{4},\s)+(ex ex\d{4})$', 'heading_exclusion_list'),  # ex ex6202, ex ex6204, ex ex6206
    (r'^ex ex(?P<heading_num>\d{4})$', 'heading_exclusion'),  # ex ex7616
    (r'^ex ex(?P<start_heading>\d{4})-ex ex(?P<end_heading>\d{4})$', 'heading_exclusion_range'),  # ex ex4410-ex ex4413

    (r'^Chapter (?P<chapter_num>\d{1,2})$', 'chapter'),
    (r'^(?P<start_heading>\d{4})-(?P<end_heading>\d{4})$', 'heading_range'),  # 1507-1515
    (r'^(\d{4},\s)+$', 'heading_list'),  # 4107, 4112
    (r'^(?P<heading_num>\d{4})', 'heading'),
]

# re.search(r'^ex ex(?P<start_heading>\d{4})-ex ex(?P<end_heading>\d{4})$', 'ex ex2004, ex ex2005')


def get_keys(st, category, match_obj):

    if category == 'chapter':
        chapter_num = match_obj.groupdict()['chapter_num']
        if len(chapter_num) == '1':
            chapter_num = '0' + chapter_num
        return ['chapter__' + chapter_num]

    elif category == 'chapter_exclusion':
        chapter_num = match_obj.groupdict()['chapter_num']
        if len(chapter_num) == '1':
            chapter_num = '0'+chapter_num
        return ['chapter_exclusion__' +chapter_num]

    elif category == 'heading':
        return ['heading__' + match_obj.groupdict()['heading_num']]

    elif category == 'heading_exclusion':
        return ['heading_exclusion__' + match_obj.groupdict()['heading_num']]

    elif category == 'heading_exclusion_list':
        heading_strings = match_obj.groups()
        keys = []
        for heading_str in heading_strings:
            heading_num = heading_str.lstrip('ex ex').strip().rstrip(',')
            keys.append('heading_exclusion__'+heading_num)
        return keys

    elif category == 'heading_exclusion_range':
        di = match_obj.groupdict()
        start, end = int(di['start_heading']), int(di['end_heading'])
        keys = []
        for heading_num in range(start, end+1):
            keys.append('heading_exclusion__%s' % heading_num)
        return keys

    elif category == 'heading_range':
        di = match_obj.groupdict()
        start, end = int(di['start_heading']), int(di['end_heading'])
        keys = []
        for heading_num in range(start, end+1):
            keys.append('heading__'+str(heading_num))
        return keys

    import pdb; pdb.set_trace()
    return ''

from commodities.models import Commodity

ROO_FP = '/Users/rossrochford/code/DIT/dit-helpdesk/dit_helpdesk/core/management/commands/roo.json'
RULES_OF_ORIGIN_DATA = json.loads(open(ROO_FP).read())


class Command(BaseCommand):

    def handle(self, *args, **options):

        for commodity in Commodity.objects.all():

            heading = commodity.get_heading()
            heading_code = heading.heading_code[:4]
            chapter_code = heading.chapter.chapter_code[:2]
            roo_keys = [
                'heading__' + heading_code, 'heading_exclusion__' + heading_code,
                'chapter__' + chapter_code.lstrip('0'), 'chapter_exclusion__' + chapter_code.lstrip('0')
                # todo: fix json file instead of stripping zeros here
            ]
            roo_fragments = []
            for key in roo_keys:
                if key in RULES_OF_ORIGIN_DATA:
                    roo_fragments.extend(RULES_OF_ORIGIN_DATA[key])

            if len(roo_fragments) > 1:
                import pdb; pdb.set_trace()
                print()


        exit()

        #url = 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=uriserv:OJ.L_.2013.054.01.0003.01.ENG'
        #resp = requests.get(url)
        #html = resp.content.decode()

        html = open(roo_fp).read()

        soup = BeautifulSoup(html, 'html.parser')
        tbody = [ch for ch in [e for e in soup.find('div', {'id': 'L_2013054EN.01003001'}).children][5].children][9]

        rows = [e for e in tbody.findChildren('tr', recursive=False)]

        table_segments = defaultdict(list)

        prev_left_col = None
        for i, row in enumerate(rows):
            if i < 2:
                continue
            cols = row.findChildren('td', recursive=False)
            left_col = cols[0].p.text.replace('\xa0', ' ').strip()
            if len(cols) != 4:
                continue

            if left_col in table_segments:
                import pdb; pdb.set_trace()

            table_segments[left_col].append(i)
            if prev_left_col and (i-1) not in table_segments[prev_left_col]:
                table_segments[prev_left_col].append(i-1)

        html_fragments = defaultdict(list)

        curr_match = None
        for segment_title, row_positions in table_segments.items():

            if segment_title in ('ex ex7218, 7219 to 7222', 'ex ex7224, 7225 to 7228'):
                continue

            segment_title = segment_title.replace(' and ', ', ')
            segment_title = segment_title.replace(' to ', '-')

            for regex, category in ROW_CATEGORY_REGEXPS:
                curr_match = re.search(regex, segment_title)
                if curr_match:
                    keys = get_keys(table_segments, category, curr_match)
                    for key in keys:
                        for row_pos in row_positions:
                            html_fragments[key].append(
                                str(rows[row_pos])
                            )
                    break

            if curr_match is None:
                import pdb; pdb.set_trace()
                print()

        file = open('/Users/rossrochford/code/DIT/dit-helpdesk/dit_helpdesk/core/management/commands/roo.json', 'w')
        file.write(json.dumps(html_fragments))
        file.close()

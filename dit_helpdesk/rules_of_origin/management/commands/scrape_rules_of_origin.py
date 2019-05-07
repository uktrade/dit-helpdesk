#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from collections import defaultdict
import json
import re
import os

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.conf import settings

# ROO_FP = os.path.join(
#     # settings.BASE_DIR, 'rules_of_origin/management/commands/roo_chile.json'
#     settings.BASE_DIR, 'rules_of_origin/management/commands/L_2013054EN.01000301.json'
# )
# RULES_OF_ORIGIN_DATA = json.loads(open(ROO_FP).read())
#
# RULES = defaultdict(list)
# EXCLUSION_RULES = defaultdict(list)
#
roo_fp = 'rules_of_origin/management/commands/roo_chile.html'


# roo_fp = 'rules_of_origin/management/commands/L_2013054EN.01000301.html'
# roo_fp = 'rules_of_origin/management/commands/Official.html'
# roo_fp = 'rules_of_origin/html_source/EUR-Lex-32015R2446-EN-EUR-Lex.html'


'''

Example keys:

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
---------

NOTE: this script doesn't parse these cases:  (which are in fact in the document)
5004 to ex ex5006
ex ex7218, 7219 to 7222
ex ex7224, 7225 to 7228
8403 and ex ex8404
'''

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


def get_keys(st, category, match_obj):

    if category == 'chapter':
        chapter_num = match_obj.groupdict()['chapter_num']
        if len(chapter_num) == '1':
            chapter_num = '0' + chapter_num
        return ['chapter__' + chapter_num]

    elif category == 'chapter_exclusion':
        chapter_num = match_obj.groupdict()['chapter_num']
        if len(chapter_num) == '1':
            chapter_num = '0' + chapter_num
        return ['chapter_exclusion__' + chapter_num]

    elif category == 'heading':
        return ['heading__' + match_obj.groupdict()['heading_num']]

    elif category == 'heading_exclusion':
        return ['heading_exclusion__' + match_obj.groupdict()['heading_num']]

    elif category == 'heading_exclusion_list':
        heading_strings = match_obj.groups()
        keys = []
        for heading_str in heading_strings:
            heading_num = heading_str.lstrip('ex ex').strip().rstrip(',')
            keys.append('heading_exclusion__' + heading_num)
        return keys

    elif category == 'heading_exclusion_range':
        di = match_obj.groupdict()
        start, end = int(di['start_heading']), int(di['end_heading'])
        keys = []
        for heading_num in range(start, end + 1):
            keys.append('heading_exclusion__%s' % heading_num)
        return keys

    elif category == 'heading_range':
        di = match_obj.groupdict()
        start, end = int(di['start_heading']), int(di['end_heading'])
        keys = []
        for heading_num in range(start, end + 1):
            keys.append('heading__' + str(heading_num))
        return keys
    return ''


class Command(BaseCommand):
    # origin_id : 'L_2013054EN.01003001'
    def handle(self, *args, **options):
        print("HANDLE")
        # html from: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=uriserv:OJ.L_.2013.054.01.0003.01.ENG
        html = open(roo_fp).read()
        soup = BeautifulSoup(html, 'html.parser')
        tbody = [ch for ch in [e for e in soup.find('div', {'id': 'L_2013054EN.01003001'}).children][5].children][9]
        # tbody = [ch for ch in [e for e in soup.find('div', {'id': 'L_2012111EN.01104601'}).children][5].children][9]
        # tbody = [ch for ch in [e for e in soup.find('div', {'id': 'L_2015343EN.01011101'}).children][5].children][9]

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

            table_segments[left_col].append(i)
            if prev_left_col and (i - 1) not in table_segments[prev_left_col]:
                table_segments[prev_left_col].append(i - 1)

        html_fragments = defaultdict(list)
        print("table_segments: ", table_segments)

        for segment_title, row_positions in table_segments.items():

            if segment_title in ('ex ex7218, 7219 to 7222', 'ex ex7224, 7225 to 7228'):
                continue  # todo: we need to include these

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

        file = open('rules_of_origin/management/commands/roo_chile.json', 'w')
        # file = open('rules_of_origin/management/commands/L_2013054EN.01000301.json', 'w')
        # file = open('rules_of_origin/management/commands/official.json', 'w')
        # file = open('rules_of_origin/data/EUR-Lex-32015R2446-EN-EUR-Lex.json', 'w')
        file.write(json.dumps(html_fragments))
        file.close()

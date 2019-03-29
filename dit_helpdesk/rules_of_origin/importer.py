import json
import re
import sys
from pprint import pprint

from django.conf import settings
from django.shortcuts import _get_queryset
from bs4 import BeautifulSoup, Tag

from hierarchy.models import Chapter, Heading

CHAPTER_MATCHES = (
    ('^ex Chapter (?P<chapter_num>\d{1,2})$', 'chapter_exclusion'),  # ex Chapter 4
    ('^(ex\xa0ex\d{4}\s)+(ex\xa0ex\d{4})$', 'heading_exclusion_list'),  # ex ex6202, ex ex6204, ex ex6206
    ('^ex\xa0ex(?P<heading_num>\d{4})$', 'heading_exclusion'),  # ex ex7616
    ('^ex\xa0ex(?P<start_heading>\d{4})( to | and |-| - )ex\xa0ex(?P<end_heading>\d{4})$', 'heading_exclusion_range'),  # ex ex4410-ex ex4413
    ('^(ex\xa0ex(?P<heading_num>\d{4}),\s)(?P<start_heading>\d{4}) to (?P<end_heading>\d{4})$', 'heading_list_exclusion_and_range'), # 'ex ex7218, 7219 to 7222'
    ('^Chapter (?P<chapter_num>\d{1,2})$', 'chapter'),
    ('^(?P<start_heading>\d{4})( to | and |-| - )(?P<end_heading>\d{4})$', 'heading_range'),  # 1507-1515
    ('^(\d{4},\s)+$', 'heading_list'),  # 4107, 4112
    ('^(?P<heading_num>\d{4})', 'heading')
)

CHAPTER_DICT = {}

def get_object_or_none(klass, *args, **kwargs):
  queryset = _get_queryset(klass)
  try:
    return queryset.get(*args, **kwargs)
  except queryset.model.DoesNotExist:
    return None


class RulesOfOriginImporter:

    def __init__(self):
        self.data = []

    def data_loader(self, file_path):
        with open(file_path) as f:
            json_data = json.load(f, )
        return json_data

    def instance_builder(self, regulations, data):

        pass

    def normalise_commodity_code(self, data):
        if len(str(data['commodity_id'])) == 9:
            commodity_code = "0{0}".format(data['commodity_id'])
        else:
            commodity_code = str(data['commodity_id'])
        return commodity_code

    def rename_key(self, old_dict, old_name, new_name):
        new_dict = {}
        for key, value in zip(old_dict.keys(), old_dict.values()):
            new_key = key if key != old_name else new_name
            new_dict[new_key] = old_dict[key]
        return new_dict

    def load(self, data_file=None):
        data_path = settings.RULES_OF_ORIGIN_DATA_PATH
        table_row_html = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{4}</td></tr>"
        if data_path:
            rules_of_origin_file = data_path.format(data_file)

            rules = self.data_loader(rules_of_origin_file)
            for rule in rules:
                for row in rules[rule]:
                    CHAPTER_DICT[row['number']] = {}
                    for item in row['row']:
                        level = self.process_id(item)

                        if level is not None:
                            item['match'] = level[0]
                            item = self.set_relationships(item)
                            if level[1] in CHAPTER_DICT[row['number']].keys() and \
                                    len(CHAPTER_DICT[row['number']][level[1]]) > 0:
                                CHAPTER_DICT[row['number']][level[1]].append(item)
                            else:
                                CHAPTER_DICT[row['number']][level[1]] = [item]
                    #
                    #     print("\t", item['id'])
                    #     print("\t", item['desc'])
                    #     print("\t", item['workingLeft'])
                    #     print("\t", item['workingRight'])

                # pprint([{ch: list(CHAPTER_DICT[ch].keys())} for ch in CHAPTER_DICT])
            # pprint(CHAPTER_DICT)

    def process_id(self, item):
        matches = [(re.search(pattern, item['id']), category) for pattern, category in CHAPTER_MATCHES
               if re.search(pattern, item['id']) is not None]
        if len(matches) > 0:
            # print("start_heading:", matches[0][0].groupdict())
            return matches[0]
        # for pattern, category in CHAPTER_MATCHES:
        #     m = re.search(pattern, item['id'])
        #     if m is not None:
        #         print(category, m)
            # if re.match(match[0], item['id']):
            #     return category, item

    def set_relationships(self, item):
        matched = item['match']
        match_results = item['match'].groupdict()
        parent_list = None

        if 'ex' in matched.string:
            item['exclusion'] = True
        else:
            item['exclusion'] = False

        if 'chapter_num' in match_results.keys():
            chapter_code = '{0:02d}'.format(int(matched.group('chapter_num'))).ljust(10, '0')
            print(chapter_code)
            parent_list = list(Chapter.objects.filter(chapter_code=chapter_code))
            print(parent_list)
        # elif 'heading_num' and 'start_heading' and 'end_heading' in match_results.keys():
        #     heading_code = '{0:02d}'.format(int(matched.group('heading_num'))).ljust(10, '0')
        #     heading = Heading.objects.filter(heading_code=heading_code)
        #     object_range = ['{0:02d}'.format(i).ljust(10, '0') for i in
        #                 range(int(matched.group('start_heading')), int(matched.group('end_heading')) + 1)]
        #     heading_list = list(Heading.objects.filter(heading_code__in=object_range))
        #     item['parents'] = heading_list+heading

        elif 'start_heading' and 'end_heading' in match_results.keys():
            start_heading_code = '{0:02d}'.format(int(matched.group('start_heading'))).ljust(10, '0')
            end_heading_code = '{0:02d}'.format(int(matched.group('end_heading'))).ljust(10, '0')

            if ' to ' in matched.string:
                object_range = ['{0:02d}'.format(i).ljust(10, '0') for i in range(int(matched.group('start_heading')), int(matched.group('end_heading'))+1)]
                parent_list = list(Heading.objects.filter(heading_code__in=object_range))
            elif ' and ' in matched.string:
                parent_list = [Heading.objects.filter(heading_code=start_heading_code), Heading.objects.filter(heading_code=end_heading_code)]
            else:
                print("MATCH TYPE: ", matched.match())

        elif 'heading_num' in match_results.keys():
            heading_code = '{0:02d}'.format(int(matched.group('heading_num'))).ljust(10, '0')
            parents = list(Heading.objects.filter(heading_code=heading_code))
            if parent_list is not None:
                parent_list.insert(0, parents[0])
            else:
                parent_list = parents

        else:
            print("MATCHED: ", match_results, matched.groupdict())
            pprint(item)
            print()

        item['parents'] = parent_list

        return item

# importer = RulesOfOriginImporter()
#
# importer.load()
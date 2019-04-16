import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from pprint import pprint

import pandas
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import _get_queryset
from numpy import nan

from countries.models import Country
from hierarchy.models import Chapter, Heading
from rules_of_origin.models import Rule, RulesDocument, RulesGroup, RulesGroupMember, RulesDocumentFootnote

CHAPTER_MATCHES = (
    ('^ex Chapter (?P<chapter_num>\d{1,2})$', 'chapter_exclusion'),  # ex Chapter 4
    ('^(ex\xa0ex\d{4}\s)+(ex\xa0ex\d{4})$', 'heading_exclusion_list'),  # ex ex6202, ex ex6204, ex ex6206
    ('^ex\xa0ex(?P<heading_num>\d{4})$', 'heading_exclusion'),  # ex ex7616
    ('^ex\xa0ex(?P<start_heading>\d{4})( to | and |-| - )ex\xa0ex(?P<end_heading>\d{4})$', 'heading_exclusion_range'),
    # ex ex4410-ex ex4413
    ('^(ex\xa0ex(?P<heading_num>\d{4}),\s)(?P<start_heading>\d{4}) to (?P<end_heading>\d{4})$',
     'heading_list_exclusion_and_range'),  # 'ex ex7218, 7219 to 7222'
    ('^Chapter (?P<chapter_num>\d{1,2})$', 'chapter'),
    ('^(?P<start_heading>\d{4})( to | and |-| - )(?P<end_heading>\d{4})$', 'heading_range'),  # 1507-1515
    ('^(\d{4},\s)+$', 'heading_list'),  # 4107, 4112
    ('^(?P<heading_num>\d{4})', 'heading')
)

MSWORD_PRIVATE_UNICODE_CHARS = {
    u'\uf0b7': "&#45;"
}


def get_object_or_none(klass, *args, **kwargs):
    """
    get and object from a given class
    :param klass:
    :param args:
    :param kwargs:
    :return:
    """

    queryset = _get_queryset(klass)

    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


class RulesOfOriginImporter:

    def __init__(self):
        self.data = {}
        self.rules_groups = {}
        self.rules_documents = {}
        self.working_group_name = None
        self.current_chapter_code = None
        self.priority = None
        self.footnotes = {}

    def data_loader(self, file_path):
        """

        :param file_path:
        :return:
        """

        extension = Path(file_path).suffix

        if extension == '.json':
            with open(file_path) as f:
                json_data = json.load(f, )
            return json_data
        else:
            with open(file_path) as f:
                data_frame = pandas.read_csv(f, encoding='utf8')
            return data_frame

    def data_writer(self, file_path, data):
        """

        :param file_path:
        :param data:
        :return:
        """

        outfile = open(file_path, 'w+')
        json.dump(data, outfile)

    def instance_builder(self):
        """

        :param regulations:
        :param data:
        :return:
        """

        rules_group, created = RulesGroup.objects.get_or_create(
            description=self.working_group_name,
        )

        if created:
            print("{} instance created".format(rules_group._meta.model_name))
        else:
            print("{} instance already exists".format(rules_group._meta.model_name))

        for country_code in self.rules_groups[self.working_group_name]:
            try:
                country = Country.objects.get(country_code=country_code)

                group_member, created = RulesGroupMember.objects.get_or_create(
                    rules_group=rules_group,
                    country=country,
                    start_date=datetime.today()
                )
                if created:
                    print("{0} instance created".format(group_member._meta.model_name))
                else:
                    print("{0} instance already exists".format(group_member._meta.model_name))
            except ObjectDoesNotExist as odne:
                print("{0} does not exist {1}".format(country_code, str(odne)))

        try:
            doc_url = self.rules_documents[self.working_group_name]
        except Exception as ex:
            print(ex.args)
            doc_url = None

        rules_document, created = RulesDocument.objects.get_or_create(
            description="{0} Rules of Origin Document".format(self.working_group_name),
            rules_group=rules_group,
            source_url=doc_url
        )

        if created:
            print("{0} instance created".format(rules_document._meta.model_name))
        else:
            print("{0} instance already exists".format(rules_document._meta.model_name))

        if self.footnotes:
            for footnote in self.footnotes:

                footnote, created = RulesDocumentFootnote.objects.get_or_create(
                    number=footnote,
                    link_html=self.footnotes[footnote]['anchor'],
                    note=self.footnotes[footnote]["note"],
                    rules_document=rules_document
                )

                if created:
                    print("{0} instance created".format(footnote._meta.model_name))
                else:
                    print("{0} instance already exists".format(footnote._meta.model_name))

        for rules_chapter in self.data:

            for level in self.data[rules_chapter]:

                for rule in self.data[rules_chapter][level]:

                    try:
                        related_chapter = Chapter.objects.get(chapter_code=rule['chapter_code'])
                    except ObjectDoesNotExist as odne:
                        print(odne.args)
                        related_chapter = None

                    rule_instance, created = Rule.objects.get_or_create(
                        rule_id=rule['id'],
                        description="".join(["<p>{0}</p>".format(text)
                                             for text in rule['description']]) if len(rule['description']) > 0 else "",
                        is_exclusion=rule['exclusion'],
                        working_or_processing_one="".join(["<p>{0}</p>".format(text)
                                                           for text in rule['workingLeft']])
                        if len(rule['workingLeft']) > 0 else "",
                        working_or_processing_two="".join(["<p>{0}</p>".format(text)
                                                           for text in rule['workingRight']])
                        if len(rule['workingRight']) > 0 else "",
                        chapter=related_chapter,
                        rules_document=rules_document
                    )
                    if created:
                        print("{0} instance created".format(rule_instance._meta.model_name))
                    else:
                        print("{0} instance already exists".format(rule_instance._meta.model_name))

    def normalise_commodity_code(self, data):
        """

        :param data:
        :return:
        """
        if len(str(data['commodity_id'])) == 9:
            commodity_code = "0{0}".format(data['commodity_id'])
        else:
            commodity_code = str(data['commodity_id'])
        return commodity_code

    def convert_ms_word_unicode_char(self, char):
        return MSWORD_PRIVATE_UNICODE_CHARS[char]

    def text_sanitiser(self, text):
        for key in MSWORD_PRIVATE_UNICODE_CHARS.keys():
            if re.match(key, text) is not None:
                text.replace(key, MSWORD_PRIVATE_UNICODE_CHARS[key])
        return text

    def rename_key(self, old_dict, old_name, new_name):
        """

        :param old_dict:
        :param old_name:
        :param new_name:
        :return:
        """
        new_dict = {}
        for key, value in zip(old_dict.keys(), old_dict.values()):
            new_key = key if key != old_name else new_name
            new_dict[new_key] = old_dict[key]
        return new_dict

    def load(self, input_file=None, output_file=None, priority=None):
        """
        Starting point of the class. Takes passed documents and loads the data into memory, processes the data
        data into organised data structures then creates the model instances and commits to the database and outputs a log
        of the data structure for review
        :param input_file: rules from rules document to be processed
        :param output_file: location of output log
        :return:
        """
        print("importing file:", input_file)
        print("priority:", priority)

        self.priority = priority

        self.set_group_documents(self.data_loader(settings.RULES_OF_ORIGIN_DOCUMENTS_FILE))
        self.set_rules_groups(self.data_loader(settings.RULES_OF_ORIGIN_GROUPS_FILE))

        self.working_group_name = Path(input_file).stem.upper()

        if self.working_group_name not in self.rules_groups.keys():
            print("{0} is not part of the Priority {1} group so there will no data to import".format(
                Path(input_file).name, priority))
            return

        if input_file:
            rules_of_origin_file = input_file

            rules = self.data_loader(rules_of_origin_file)

            self.process_rules(rules['chapters'])

            if rules['footnotes']:
                self.process_footnotes(rules['footnotes'])

            self.instance_builder()

            # self.data_writer(data_path.format("{0}/{1}".format(data_path, output_file)), self.data)

    def process_footnotes(self, footnotes):

        for idx, footnote in enumerate(footnotes):
            self.footnotes[idx+1] = footnote

    def set_rules_groups(self, groups_data):
        """
        Using the data passed in csv file `groups_file` mapping the prioritised list of countries and groups
        build the data structure used to build the model instances and commit them to the database
        :param groups_data: list of countries mapped to rule groups tagged by priority
        """

        country_codes = list(groups_data.Code)
        groups_priority_one = list(groups_data['Priority 1'])
        groups_priority_two = list(groups_data['Priority 2'])

        groups = groups_priority_one if self.priority == 1 else groups_priority_two

        for idx, group in enumerate(groups):
            if group is not nan:

                if " and " in group:
                    for grp in group.split(' and '):
                        self.build_rules_groups(country_codes, grp, idx)
                else:
                    self.build_rules_groups(country_codes, group, idx)

    def build_rules_groups(self, country_codes, group, idx):
        """
        helper method used by `set_rules_groups` to build the main dictionary data structure used by instance builder
        :param country_codes: country codes lookup
        :param group: current group to work with in this iteration
        :param idx: current idx used to lookup coutry codes
        """
        group = group.replace(' ', '_').upper()
        if group in self.rules_groups.keys() and isinstance(self.rules_groups[group], list):
            self.rules_groups[group].append(country_codes[idx])
        else:
            self.rules_groups[group] = [country_codes[idx]]

    def set_group_documents(self, documents_data):
        """
        Using the data passed in csv file `documents_file` build the data structure for the
        variable holding the mapping of rule groups to document urls
        :param documents_data:
        """
        groups = list(documents_data.Group)
        documents = list(documents_data.Document)
        for idx, group in enumerate(groups):
            self.rules_documents[groups[idx]] = documents[idx]

    def process_rules(self, rules):
        """
        Process rules of origin data loaded into memry from the file system data and prepares it for the instance builder
        :param rules:
        :return:
        """

        for rule in rules:

            self.data[rule['number']] = {}

            chapter_code = self.get_hierarchy_code(rule['number'], "Chapter")

            for item in rule['rows']:
                regex_match, level = self.match_hierarchy_level(item['id'])

                if regex_match is not None:
                    item = self.set_relationships(item, regex_match, chapter_code)
                    if level in self.data[rule['number']].keys() and \
                            len(self.data[rule['number']][level]) > 0:
                        self.data[rule['number']][level].append(item)
                    else:
                        self.data[rule['number']][level] = [item]

    def match_hierarchy_level(self, item_id):
        """
        Match item id to level and category
        :param item:
        :return:
        """
        # print("item_id: ", item_id[0], [pattern for pattern, category in CHAPTER_MATCHES])
        matches = [(re.search(pattern, item_id[0]), category) for pattern, category in CHAPTER_MATCHES
                   if re.search(pattern, item_id[0]) is not None]
        if len(matches) > 0:
            return matches[0]
        else:
            return (None, None)

    def set_relationships(self, item, regex_match, chapter_code):
        """

        Sets teh relationship of a rule to the hierarchy structure

        :param item:
        :param regex_match:
        :return:
        """

        match_results = regex_match.groupdict()

        parent_ids_list = None

        item['exclusion'] = True if 'ex' in regex_match.string else False

        related_hierarchy_levels = None

        if {'chapter_num', } <= set(match_results.keys()):
            chapter_code = self.get_hierarchy_code(regex_match.group('chapter_num'), "Chapter")
            related_hierarchy_levels = self.get_related_hierarchy_levels("Chapter", chapter_code, item, parent_ids_list)

        elif {'heading_num', 'start_heading', 'end_heading'} <= set(match_results.keys()):
            heading_code = self.get_hierarchy_code(regex_match.group('heading_num'), "Heading")

            start_heading_code = '{0}'.format(regex_match.group('start_heading')).ljust(10, '0')
            end_heading_code = '{0}'.format(regex_match.group('end_heading')).ljust(10, '0')

            code_range = [self.get_hierarchy_code(i, "Heading") for i in
                          range(int(regex_match.group('start_heading')), int(regex_match.group('end_heading')) + 1)]

            related_range = self.get_related_hierarchy_levels("Heading", start_heading_code,
                                                              end_code=end_heading_code,
                                                              code_range=code_range)
            related = self.get_related_hierarchy_levels("Heading", heading_code)
            related_hierarchy_levels = related + related_range

        elif {'start_heading', 'end_heading'} <= set(match_results.keys()) \
                and not {'heading_num'} <= set(match_results.keys()):

            start_heading_code = '{0}'.format(regex_match.group('start_heading')).ljust(10, '0')
            end_heading_code = '{0}'.format(regex_match.group('end_heading')).ljust(10, '0')

            if ' to ' in regex_match.string:
                code_range = [self.get_hierarchy_code(i, "Heading") for i in
                              range(
                                  int(regex_match.group('start_heading')),
                                  int(regex_match.group('end_heading')) + 1
                              )]
                related_hierarchy_levels = self.get_related_hierarchy_levels("Heading", start_heading_code,
                                                                             end_code=end_heading_code,
                                                                             code_range=code_range)

            elif ' and ' in regex_match.string:
                code_range = [self.get_hierarchy_code(i, "Heading") for i in
                              range(
                                  int(regex_match.group('start_heading')),
                                  int(regex_match.group('end_heading')) + 1
                              )]
                related_hierarchy_levels = self.get_related_hierarchy_levels("Heading", start_heading_code,
                                                                             end_code=end_heading_code,
                                                                             code_range=code_range)

            else:
                print("MATCH TYPE: ", regex_match.groupdict())

        elif {'heading_num', } <= set(match_results.keys()):

            heading_code = self.get_hierarchy_code(regex_match.group('heading_num'), "Heading")
            related_hierarchy_levels = self.get_related_hierarchy_levels("Heading", heading_code)

        else:
            print(item['id'], regex_match.groupdict())

        self.clean_id(item)

        item['chapter_code'] = chapter_code

        item['hierarchy_relations'] = related_hierarchy_levels

        return item

    def get_hierarchy_code(self, code, level):
        """
        Helper method to derive the 10 digit, heading or chapter, code given a match pattern
        and a 2 or 4 digit code
        :param code:
        :param level:
        :return:
        """
        if level == "Chapter":
            return '{0:02d}'.format(int(code)).ljust(10, '0')
        else:
            return '{0}'.format(code).ljust(10, '0')

    def clean_id(self, item):
        """
        Helper method to clean non utf-8 character from the rule id column
        :param item:
        :return:
        """
        item['id'] = item['id'][0].replace('ex\xa0ex', 'ex ')

    def get_related_hierarchy_levels(self, type, code, end_code=None, code_range=None):
        """
        get related hierarchy objects according to rule code and code ranges

        :param type: Chapter or Heading level rule
        :param code: 10 digit code used to lookup Objects in the database
        either single or start code of a range
        :param end_code: end 10 digit code of a range
        :param code_range: list of codes in the range
        :return: a list of related dictionary objects
        """

        related_objects = {}
        if type == "Chapter":
            related_objects = list([{"id": chapter.id,
                                     "chapter_code": chapter.chapter_code,
                                     "desription": chapter.description,
                                     "type": type
                                     } for chapter in Chapter.objects.filter(chapter_code=code)])
        elif type == "Heading":
            if code_range:
                related_objects = list([{"id": heading.id,
                                         "heading_code": heading.heading_code,
                                         "description": heading.description,
                                         "type": type
                                         } for heading in Heading.objects.filter(heading_code__in=code_range)])

            elif end_code:
                related_objects = [{"id": heading.id,
                                    "heading_code": heading.heading_code,
                                    "descriptipn": heading.description,
                                    "type": type
                                    } for heading in Heading.objects.filter(heading_code=code)] + [{
                    "id": heading.id,
                    "heading_code": heading.heading_code,
                    "descriptipn": heading.description,
                    "type": type
                } for heading in Heading.objects.filter(heading_code=end_code)]
            else:
                related_objects = [{"id": heading.id,
                                    "heading_code": heading.heading_code,
                                    "descriptipn": heading.description,
                                    "type": type
                                    } for heading in Heading.objects.filter(heading_code=code)]
        else:
            print("no level")

        return related_objects

from datetime import datetime
import re
from dateutil.parser import parse as parse_dt

from django.conf import settings
from django.urls import reverse

COMMODITY_URL = (
    'https://www.trade-tariff.service.gov.uk/trade-tariff/'
    'commodities/%s.json?currency=EUR&day=1&month=1&year=2019'
)
CHAPTER_URL = 'https://www.trade-tariff.service.gov.uk/trade-tariff/chapters/%s.json'
HEADING_URL = 'https://www.trade-tariff.service.gov.uk/trade-tariff/headings/%s.json'


DUTY_HTML_REGEX = r'<span.*>\s?(?P<duty>\d[\d\.]*?)\s?</span>'

COMMODITY_DETAIL_TABLE_KEYS = [
    # dict_key, column_title
    ('country', 'Country'),
    ('measure_description', 'Measure type'),
    ('measure_value', 'Value'),
    ('conditions_html', 'Conditions'),
    ('excluded_countries', 'Excluded Countries'),
    ('start_end_date', 'Date'),
    # ('legal_base_html', 'Legal Base'),
    # ('footnotes_html', 'Footnotes'),
]


class CommodityJson(object):

    def __init__(self, di):
        self.di = di

    def __repr__(self):
        return 'CommodityJson'

    @property
    def title(self):
        return self.di['description']

    @property
    def heading_description(self):
        return self.di['heading']['description']

    @property
    def code(self):
        return self.di['goods_nomenclature_item_id']

    @property
    def chapter_note(self):
        return self.di['chapter']['chapter_note']

    @property
    def chapter_title(self):
        return self.di['chapter']['formatted_description']

    @property
    def section_position(self):
        return self.di['section']['position']

    @property
    def duty_rate(self):
        duty_html = self.di['basic_duty_rate']
        match = re.search(DUTY_HTML_REGEX, duty_html, flags=re.I)
        if match is None:
            return None
        return float(match.groupdict()['duty'])  # percentage

    def get_import_measures(self, origin_country, vat=None, excise=None):

        measures = [
            ImportMeasureJson(d, self.code) for d in self.di['import_measures']
        ]
        measures = [
            json_obj for json_obj in measures
            if json_obj.is_relevant_for_origin_country(origin_country)
        ]

        if vat is not None:
            measures = [obj for obj in measures if obj.vat == vat]
        if excise is not None:
            measures = [obj for obj in measures if obj.excise == excise]

        return measures

    def get_import_measure_by_id(self, measure_id, country_code=None):
        measures = [
            measure for measure in self.get_import_measures(country_code) if measure.measure_id == measure_id
        ]
        if len(measures) > 1:
            print("query returned {0} results. There should be only only one".format(len(measures)))
        elif len(measures)== 1:
            return measures[0]
        else:
            return None

class CommodityHeadingJson(object):
    """
    Sub-dictionary from Commodity response about its Heading
    example:
    {'goods_nomenclature_item_id': '0706000000',
    'description': 'Carrots, turnips, salad beetroot, salsify, celeriac, radishes '
                   'and similar edible roots, fresh or chilled',
     'formatted_description': 'Carrots, turnips, salad beetroot, salsify, celeriac, radishes '
                              'and similar edible roots, fresh or chilled',
     'description_plain': 'Carrots, turnips, salad beetroot, salsify, celeriac, radishes '
                          'and similar edible roots, fresh or chilled'}
    ('basic_duty_rate', "<span title='13.6 '>13.60</span> %")
    """

    def __init__(self, di):
        self.di = di

    @property
    def title(self):
        return self.di['description']

    @property
    def harmonized_code(self):
        return self.di['goods_nomenclature_item_id']

class SectionJson(object):

    def __init__(self, di):
        self.di = di

    @property
    def title(self):
        return self.di['title']

    @property
    def chapter_ids(self):
        frm, to = int(self.di['chapter_from']), int(self.di['chapter_to'])
        return [v for v in range(frm, to + 1)]

    @property
    def chapter_urls(self):
        return [
            CHAPTER_URL % "{:02d}".format(id) for id in self.chapter_ids
        ]

    @property
    def id(self):
        return self.di['id']

    @property
    def position(self):
        return self.di['position']

    @property
    def numeral(self):
        return self.di['numeral']


class ChapterJson(object):

    def __init__(self, di):
        self.di = di

    @property
    def title(self):
        return self.di['formatted_description']

    @property
    def harmonized_code(self):
        return self.di['goods_nomenclature_item_id']

    @property
    def heading_ids(self):
        return [
            di['goods_nomenclature_item_id'][:4] for di in self.di['headings']
        ]

    @property
    def heading_urls(self):
        return [HEADING_URL % id for id in self.heading_ids]


class HeadingJson(object):

    def __init__(self, di):
        self.di = di

    @property
    def title(self):
        return self.di['formatted_description'].replace('&nbsp;', ' ').strip()

    @property
    def code(self):
        return self.di['goods_nomenclature_item_id']

    @property
    def commodity_dicts(self):
        return [di for di in self.di.get('commodities', [])]

    @property
    def commodity_ids(self):
        if 'commodities' not in self.di:
            tup = (self.code, self.title)
            print('warning: no commodities found for Heading: %s "%s"' % tup)
            return []

        return [
            (di['goods_nomenclature_item_id'], di['leaf'])
            for di in self.di['commodities']
        ]

    @property
    def commodity_urls(self):
        return [((COMMODITY_URL % _id), is_leaf) for (_id, is_leaf) in self.commodity_ids]


class ImportMeasureJson(object):

    def __init__(self, di, commodity_code):
        self.di = di
        self.commodity_code = commodity_code

    @classmethod
    def get_date(cls, di, key):
        dt_str = di.get(key)
        if dt_str is None:
            return None
        return parse_dt(dt_str)

    def __repr__(self):
        return 'ImportMeasureJson %s %s' % (self.commodity_code, self.type_id)

    @property
    def is_import(self):
        return self.di['import']

    @property
    def origin(self):
        return self.di['origin']  # e.g. "uk"

    @property
    def effective_start_date(self):
        return self.get_date(self.di, 'effective_start_date')

    @property
    def effective_end_date(self):
        return self.get_date(self.di, 'effective_end_date')

    @property
    def geographical_area(self):
        """"
        one GA per measure
        if everywhere in the world outside the EU return ERGA OMNES

        """

        if self.di['geographical_area']['description'] == 'ERGA OMNES':
            return 'ERGA OMNES'
        # NOTE: when filtering by a GA, you will need to search
        # both the top-level and any children in case the country exists
        import pdb; pdb.set_trace()

    @property
    def type_id(self):
        """
        returns type_id

        e.g. "VTZ", "VTS", "103" (103 is third world duty)
        (142, tariff preference, e.g. preferential rate for particular countries;
        122-125 quota limit)

        """
        return self.di['measure_type']['id']

    @property
    def type_description(self):
        # NOTE: localised measure type descriptions are in the dumped database
        return self.di['measure_type']['description']

    @property
    def measure_id(self):
        return self.di['measure_id']

    @property
    def conditions_summary(self):
        """
        list of conditions (e.g. you can import if you have document X)
        other keys: 'condition_code', 'condition', 'document_code', '
        requirement', 'action', 'duty_expression'
        """
        return [di['condition'] for di in self.di['measure_conditions']]

    @property
    def excluded_country_area_ids(self):
        return [
            di['geographical_area_id'] for di in self.di['excluded_countries']
        ]

    @property
    def vat(self):
        return self.di['vat']

    @property
    def excise(self):
        return self.di['excise']

    @property
    def order_number_definition_summary(self):
        if not self.di.get('order_number'):
            return None
        status = self.di['order_number']['definition']['status']
        description = self.di['order_number']['definition']['description']
        return status, description

    @property
    def num_conditions(self):
        return len(self.di['measure_conditions'])

    def is_relevant_for_origin_country(self, origin_country_code):
        geo_area = self.di['geographical_area']
        if geo_area['id'][0].isalpha() and geo_area['id'] == origin_country_code:
            return True
        for child_area in geo_area['children_geographical_areas']:
            if child_area['id'][0].isalpha() and child_area['id'] == origin_country_code:
                return True
        return False

    @property
    def vue__legal_base_html(self):
        # {'published_date': '2017-09-20', 'regulation_url': 'http://eur-lex.europa.eu/search.html?whOJ=NO_OJ%3D241,YEAR_OJ%3D2017,PAGE_FIRST%3D0001&DB_COLL_OJ=oj-l&type=advanced&lang=en', 'regulation_code': 'R1585/17', 'validity_end_date': None, 'validity_start_date': '2017-09-21T00:00:00.000Z', 'officialjournal_page': 1, 'officialjournal_number': 'L 241'} )
        if not self.di.get('legal_acts', []):  # todo: make this a property method
            return '-'
        hrefs = []
        for d in self.di['legal_acts']:
            reg_url, reg_code = d['regulation_url'], d['regulation_code']
            hrefs.append(
                '<a href="%s">%s</a>' % (reg_url, reg_code)
            )
        return ', '.join(hrefs)

    @property
    def vue__conditions_html(self):
        if not self.num_conditions:
            return '-'
        conditions_url = "{0}/import-measure/{1}/conditions".format(self.commodity_code, self.measure_id)
        return '<a href="%s">Conditions</a>' % conditions_url

    @property
    def vue__footnotes_html(self):
        # {'code': 'CD550', 'description': 'Eligibility to benefit from this tariff quota shall be subject to the presentation of an import licence AGRIM and a declaration of origin issued in accordance with Regulation (EU) 2017/1585.', 'formatted_description': 'Eligibility to benefit from this tariff quota shall be subject to the presentation of an import licence AGRIM and a declaration of origin issued in accordance with Regulation (EU) 2017/1585.'}
        if not self.di['footnotes']:
            return '-'

        hrefs = []
        for d in self.di['footnotes']:
            code, url = d['code'], '#'
            hrefs.append(
                '<a href="%s">%s</a>' % (url, code)
            )
        return ', '.join(hrefs)

    def get_table_dict(self):

        country = self.di['geographical_area']['description']

        if self.di['geographical_area']['id'][0].isalpha():
            country = country + ' (%s)' % self.di['geographical_area']['id']

        measure_description = self.di['measure_type']['description']

        if self.di['order_number']:
            order_str = ' - Order No: %s' % self.di['order_number']['number']  # todo: add href
            measure_description = measure_description + '\n' + order_str

        measure_value = self.di['duty_expression']['base']

        excluded_countries = ', '.join([
            di['description'] for di in self.di['excluded_countries']
        ])

        start_end_date = self.di['effective_start_date'][:10]
        if self.di.get('effective_end_date'):
            date_str = self.di['effective_end_date'][:10]
            start_end_date = start_end_date + '\n(%s)' % date_str

        return {
            'country': country, 'measure_description': measure_description,
            'conditions_html': self.vue__conditions_html, 'measure_value': measure_value,
            'excluded_countries': excluded_countries, 'start_end_date': start_end_date,
            'legal_base_html': self.vue__legal_base_html,
            'footnotes_html': self.vue__footnotes_html
        }

    def get_table_row(self):
        di = self.get_table_dict()
        data = [di[tup[0]] for tup in COMMODITY_DETAIL_TABLE_KEYS]
        data = self.rename_countries_default(data)

        try:
            data = self.reformat_date(data)
        except Exception as e:
            print(e.args)

        data_with_headings = []

        for index, value in enumerate(data):
            data_with_headings.append([COMMODITY_DETAIL_TABLE_KEYS[index][1], value])

        return data_with_headings

    def reformat_date(self, data):

        row_last_index = len(data) - 1
        pattern = '^((\d{4})-(\d{2})-(\d{2}))$|^((\d{4})-(\d{2})-(\d{2}))\s(\(((\d{4})-(\d{2})-(\d{2}))\))$'
        target = re.compile(pattern)
        matched = target.match(data[row_last_index])
        if not matched.group(9):
            start_date_obj = datetime.strptime(matched.group(1), '%Y-%m-%d')
            start_date_str = start_date_obj.strftime('%-d&nbsp;%B&nbsp;%Y')
            data[row_last_index] = start_date_str
        else:
            start_date_obj = datetime.strptime(matched.group(5), '%Y-%m-%d')
            start_date_str = start_date_obj.strftime('%-d&nbsp;%B&nbsp;%Y')
            end_date_obj = datetime.strptime(matched.group(10), '%Y-%m-%d')
            end_date_str = end_date_obj.strftime('%-d&nbsp;%B&nbsp;%Y')

            data[row_last_index] = "{0} ({1})".format(start_date_str, end_date_str)

        return data

    def rename_countries_default(self, data):
        if 'ERGA OMNES' in data:
            idx = data.index('ERGA OMNES')
            data[idx] = "All countries"
        return data

    def get_measure_conditions(self):
        return [
            MeasureCondition(di) for di in self.di['measure_conditions']
        ]

    def get_measure_conditions_by_measure_id(self, measure_id):
        return [
            condition for condition in self.get_measure_conditions() if condition.di['measure_id'] == measure_id
        ]

class MeasureCondition(object):

    def __init__(self, di):
        # keys: ['action', 'condition', 'requirement', 'document_code', 'condition_code', 'duty_expression']
        self.di = di


# ========================================
# Section response:

    """
    {'_response_info': {'links': [{'href': '/trade-tariff/sections/4.json',
                               'rel': 'self'},
                              {'href': '/trade-tariff/sections',
                               'rel': 'sections'}]},
    'chapter_from': '16',
    'chapter_to': '24',
    'chapters': [{'chapter_note_id': 65,
               'description': 'PREPARATIONS OF MEAT, OF FISH OR OF '
                              'CRUSTACEANS, MOLLUSCS OR OTHER AQUATIC '
                              'INVERTEBRATES',
               'formatted_description': 'Preparations of meat, of fish or of '
                                        'crustaceans, molluscs or other '
                                        'aquatic invertebrates',
               'goods_nomenclature_item_id': '1600000000',
               'goods_nomenclature_sid': 32656,
               'headings_from': '1601',
               'headings_to': '1605'},
              {'chapter_note_id': 66,
               'description': 'SUGARS AND SUGAR CONFECTIONERY',
               'formatted_description': 'Sugars and sugar confectionery',
               'goods_nomenclature_item_id': '1700000000',
               'goods_nomenclature_sid': 32980,
               'headings_from': '1701',
               'headings_to': '1704'},
              {'chapter_note_id': 67,
               'description': 'COCOA AND COCOA PREPARATIONS',
               'formatted_description': 'Cocoa and cocoa preparations',
               'goods_nomenclature_item_id': '1800000000',
               'goods_nomenclature_sid': 33088,
               'headings_from': '1801',
               'headings_to': '1806'},
              {'chapter_note_id': 68,
               'description': 'PREPARATIONS OF CEREALS, FLOUR, STARCH OR MILK; '
                              "PASTRYCOOKS' PRODUCTS",
               'formatted_description': 'Preparations of cereals, flour, '
                                        "starch or milk; pastrycooks' products",
               'goods_nomenclature_item_id': '1900000000',
               'goods_nomenclature_sid': 33158,
               'headings_from': '1901',
               'headings_to': '1905'},
              {'chapter_note_id': 69,
               'description': 'PREPARATIONS OF VEGETABLES, FRUIT, NUTS OR '
                              'OTHER PARTS OF PLANTS',
               'formatted_description': 'Preparations of vegetables, fruit, '
                                        'nuts or other parts of plants',
               'goods_nomenclature_item_id': '2000000000',
               'goods_nomenclature_sid': 33378,
               'headings_from': '2001',
               'headings_to': '2009'},
              {'chapter_note_id': 70,
               'description': 'MISCELLANEOUS EDIBLE PREPARATIONS',
               'formatted_description': 'Miscellaneous edible preparations',
               'goods_nomenclature_item_id': '2100000000',
               'goods_nomenclature_sid': 34458,
               'headings_from': '2101',
               'headings_to': '2106'},
              {'chapter_note_id': 71,
               'description': 'BEVERAGES, SPIRITS AND VINEGAR',
               'formatted_description': 'Beverages, spirits and vinegar',
               'goods_nomenclature_item_id': '2200000000',
               'goods_nomenclature_sid': 34628,
               'headings_from': '2201',
               'headings_to': '2209'},
              {'chapter_note_id': 72,
               'description': 'RESIDUES AND WASTE FROM THE FOOD INDUSTRIES; '
                              'PREPARED ANIMAL FODDER',
               'formatted_description': 'Residues and waste from the food '
                                        'industries; prepared animal fodder',
               'goods_nomenclature_item_id': '2300000000',
               'goods_nomenclature_sid': 35125,
               'headings_from': '2301',
               'headings_to': '2309'},
              {'chapter_note_id': 73,
               'description': 'TOBACCO AND MANUFACTURED TOBACCO SUBSTITUTES',
               'formatted_description': 'Tobacco and manufactured tobacco '
                                        'substitutes',
               'goods_nomenclature_item_id': '2400000000',
               'goods_nomenclature_sid': 35246,
               'headings_from': '2401',
               'headings_to': '2403'}],
    'id': 4,
    'numeral': 'IV',
    'position': 4,
    'title': 'Prepared foodstuffs; beverages, spirits and vinegar; tobacco and '
          'manufactured tobacco substitutes'}
    """

# ======================

# Chapter response

    """
    Chapter:

    {'_response_info': {'links': [{'href': '/trade-tariff/chapters/24.json',
                               'rel': 'self'},
                              {'href': '/trade-tariff/sections/4',
                               'rel': 'section'}]},
    'chapter_note': '* 1\\. This chapter does not cover medicinal cigarettes '
                 '(Chapter 30).',
    'chapter_note_id': 73,
    'description': 'TOBACCO AND MANUFACTURED TOBACCO SUBSTITUTES',
    'formatted_description': 'Tobacco and manufactured tobacco substitutes',
    'goods_nomenclature_item_id': '2400000000',
    'goods_nomenclature_sid': 35246,
    'headings': [{'children': [],
               'declarable': False,
               'description': 'Unmanufactured tobacco; tobacco refuse',
               'description_plain': 'Unmanufactured tobacco; tobacco refuse',
               'formatted_description': 'Unmanufactured tobacco; tobacco '
                                        'refuse',
               'goods_nomenclature_item_id': '2401000000',
               'goods_nomenclature_sid': 35247,
               'leaf': True,
               'producline_suffix': '80'},
              {'children': [],
               'declarable': False,
               'description': 'Cigars, cheroots, cigarillos and cigarettes, of '
                              'tobacco or of tobacco substitutes',
               'description_plain': 'Cigars, cheroots, cigarillos and '
                                    'cigarettes, of tobacco or of tobacco '
                                    'substitutes',
               'formatted_description': 'Cigars, cheroots, cigarillos and '
                                        'cigarettes, of tobacco or of tobacco '
                                        'substitutes',
               'goods_nomenclature_item_id': '2402000000',
               'goods_nomenclature_sid': 35283,
               'leaf': True,
               'producline_suffix': '80'},
              {'children': [],
               'declarable': False,
               'description': 'Other manufactured tobacco and manufactured '
                              "tobacco substitutes; 'homogenised' or "
                              "'reconstituted' tobacco; tobacco extracts and "
                              'essences',
               'description_plain': 'Other manufactured tobacco and '
                                    'manufactured tobacco substitutes; '
                                    "'homogenised' or 'reconstituted' tobacco; "
                                    'tobacco extracts and essences',
               'formatted_description': 'Other manufactured tobacco and '
                                        'manufactured tobacco substitutes; '
                                        "'homogenised' or 'reconstituted' "
                                        'tobacco; tobacco extracts and '
                                        'essences',
               'goods_nomenclature_item_id': '2403000000',
               'goods_nomenclature_sid': 35287,
               'leaf': True,
               'producline_suffix': '80'}],
    'section': {'id': 4,
             'numeral': 'IV',
             'position': 4,
             'title': 'Prepared foodstuffs; beverages, spirits and vinegar; '
                      'tobacco and manufactured tobacco substitutes'},
    'section_id': 4}
    """

# =======================

# Heading response

    """

    {'_response_info': {'links': [{'href': '/trade-tariff/headings/2402.json',
                               'rel': 'self'},
                              {'href': '/trade-tariff/chapters/24',
                               'rel': 'chapter'},
                              {'href': '/trade-tariff/sections/4',
                               'rel': 'section'}]},
    'bti_url': 'http://ec.europa.eu/taxation_customs/dds2/ebti/ebti_consultation.jsp?Lang=en&nomenc=2402000000&Expand=true',
    'chapter': {'chapter_note': '* 1\\. This chapter does not cover medicinal '
                             'cigarettes (Chapter 30).',
             'description': 'TOBACCO AND MANUFACTURED TOBACCO SUBSTITUTES',
             'formatted_description': 'Tobacco and manufactured tobacco '
                                      'substitutes',
             'goods_nomenclature_item_id': '2400000000'},
    'commodities': [{'description': 'Cigars, cheroots and cigarillos, containing '
                                 'tobacco',
                  'description_plain': 'Cigars, cheroots and cigarillos, '
                                       'containing tobacco',
                  'formatted_description': 'Cigars, cheroots and cigarillos, '
                                           'containing tobacco',
                  'goods_nomenclature_item_id': '2402100000',
                  'goods_nomenclature_sid': 35284,
                  'leaf': True,
                  'number_indents': 1,
                  'overview_measures': [{'duty_expression': {'base': '20.00 %',
                                                             'formatted_base': '<span '
                                                                               "title='20.0 "
                                                                               "'>20.00</span> "
                                                                               '%'},
                                         'id': -488398,
                                         'measure_type': {'description': 'VAT '
                                                                         'standard '
                                                                         'rate',
                                                          'id': 'VTS'},
                                         'vat': True},
                                        {'duty_expression': {'base': '1000 '
                                                                     'p/st',
                                                             'formatted_base': '<abbr '
                                                                               "title='1000 "
                                                                               "items'>1000 "
                                                                               'p/st</abbr>'},
                                         'id': 2982268,
                                         'measure_type': {'description': 'Supplementary '
                                                                         'unit',
                                                          'id': '109'},
                                         'vat': False},
                                        {'duty_expression': {'base': '26.00 %',
                                                             'formatted_base': '<span '
                                                                               "title='26.0 "
                                                                               "'>26.00</span> "
                                                                               '%'},
                                         'id': 2053040,
                                         'measure_type': {'description': 'Third '
                                                                         'country '
                                                                         'duty',
                                                          'id': '103'},
                                         'vat': False}],
                  'parent_sid': None,
                  'producline_suffix': '80'},
                 {'description': 'Cigarettes containing tobacco',
                  'description_plain': 'Cigarettes containing tobacco',
                  'formatted_description': 'Cigarettes containing tobacco',
                  'goods_nomenclature_item_id': '2402200000',
                  'goods_nomenclature_sid': 35285,
                  'leaf': False,
                  'number_indents': 1,
                  'parent_sid': None,
                  'producline_suffix': '80'},
                 {'description': 'Containing cloves',
                  'description_plain': 'Containing cloves',
                  'formatted_description': 'Containing cloves',
                  'goods_nomenclature_item_id': '2402201000',
                  'goods_nomenclature_sid': 55653,
                  'leaf': True,
                  'number_indents': 2,
                  'overview_measures': [{'duty_expression': {'base': '20.00 %',
                                                             'formatted_base': '<span '
                                                                               "title='20.0 "
                                                                               "'>20.00</span> "
                                                                               '%'},
                                         'id': -463662,
                                         'measure_type': {'description': 'VAT '
                                                                         'standard '
                                                                         'rate',
                                                          'id': 'VTS'},
                                         'vat': True},
                                        {'duty_expression': {'base': '1000 '
                                                                     'p/st',
                                                             'formatted_base': '<abbr '
                                                                               "title='1000 "
                                                                               "items'>1000 "
                                                                               'p/st</abbr>'},
                                         'id': 2982269,
                                         'measure_type': {'description': 'Supplementary '
                                                                         'unit',
                                                          'id': '109'},
                                         'vat': False},
                                        {'duty_expression': {'base': '10.00 %',
                                                             'formatted_base': '<span '
                                                                               "title='10.0 "
                                                                               "'>10.00</span> "
                                                                               '%'},
                                         'id': 2053041,
                                         'measure_type': {'description': 'Third '
                                                                         'country '
                                                                         'duty',
                                                          'id': '103'},
                                         'vat': False}],
                  'parent_sid': 35285,
                  'producline_suffix': '80'},
                 {'description': 'Other',
                  'description_plain': 'Other',
                  'formatted_description': 'Other',
                  'goods_nomenclature_item_id': '2402209000',
                  'goods_nomenclature_sid': 55654,
                  'leaf': True,
                  'number_indents': 2,
                  'overview_measures': [{'duty_expression': {'base': '20.00 %',
                                                             'formatted_base': '<span '
                                                                               "title='20.0 "
                                                                               "'>20.00</span> "
                                                                               '%'},
                                         'id': -488435,
                                         'measure_type': {'description': 'VAT '
                                                                         'standard '
                                                                         'rate',
                                                          'id': 'VTS'},
                                         'vat': True},
                                        {'duty_expression': {'base': '1000 '
                                                                     'p/st',
                                                             'formatted_base': '<abbr '
                                                                               "title='1000 "
                                                                               "items'>1000 "
                                                                               'p/st</abbr>'},
                                         'id': 2982269,
                                         'measure_type': {'description': 'Supplementary '
                                                                         'unit',
                                                          'id': '109'},
                                         'vat': False},
                                        {'duty_expression': {'base': '57.60 %',
                                                             'formatted_base': '<span '
                                                                               "title='57.6 "
                                                                               "'>57.60</span> "
                                                                               '%'},
                                         'id': 2053042,
                                         'measure_type': {'description': 'Third '
                                                                         'country '
                                                                         'duty',
                                                          'id': '103'},
                                         'vat': False}],
                  'parent_sid': 35285,
                  'producline_suffix': '80'},
                 {'description': 'Other',
                  'description_plain': 'Other',
                  'formatted_description': 'Other',
                  'goods_nomenclature_item_id': '2402900000',
                  'goods_nomenclature_sid': 35286,
                  'leaf': True,
                  'number_indents': 1,
                  'overview_measures': [{'duty_expression': {'base': '20.00 %',
                                                             'formatted_base': '<span '
                                                                               "title='20.0 "
                                                                               "'>20.00</span> "
                                                                               '%'},
                                         'id': -488361,
                                         'measure_type': {'description': 'VAT '
                                                                         'standard '
                                                                         'rate',
                                                          'id': 'VTS'},
                                         'vat': True},
                                        {'duty_expression': {'base': '57.60 %',
                                                             'formatted_base': '<span '
                                                                               "title='57.6 "
                                                                               "'>57.60</span> "
                                                                               '%'},
                                         'id': 2053043,
                                         'measure_type': {'description': 'Third '
                                                                         'country '
                                                                         'duty',
                                                          'id': '103'},
                                         'vat': False}],
                  'parent_sid': None,
                  'producline_suffix': '80'}],
    'description': 'Cigars, cheroots, cigarillos and cigarettes, of tobacco or of tobacco substitutes',
    'footnotes': [{'code': 'TN701',
                'description': 'According to  the Council Regulation (EU) No '
                               '692/2014 (OJ L183, p. 9) it shall be '
                               'prohibited to import into European Union goods '
                               'originating in Crimea or Sevastopol.\n'
                               'The prohibition shall not apply in respect '
                               'of: \n'
                               '(a) the execution until 26 September 2014, of '
                               'trade contracts concluded before 25 June 2014, '
                               'or of ancillary contracts necessary for the '
                               'execution of such contracts, provided that the '
                               'natural or legal persons, entity or body '
                               'seeking to perform the contract have notified, '
                               'at least 10 working days in advance, the '
                               'activity or transaction to the competent '
                               'authority of the Member State in which they '
                               'are established. \n'
                               '(b) goods originating in Crimea or Sevastopol '
                               'which have been made available to the '
                               'Ukrainian authorities for examination, for '
                               'which compliance with the conditions '
                               'conferring entitlement to preferential origin '
                               'has been verified and for which a certificate '
                               'of origin has been issued in accordance with '
                               'Regulation (EU) No 978/2012 and Regulation '
                               '(EU) No 374/2014 or in accordance with the '
                               'EU-Ukraine Association Agreement.',
                'formatted_description': 'According to  the Council Regulation '
                                         '(EU) No 692/2014 (OJ L183, p. 9) it '
                                         'shall be prohibited to import into '
                                         'European Union goods originating in '
                                         'Crimea or Sevastopol.<br/>The '
                                         'prohibition shall not apply in '
                                         'respect of: <br/>(a) the execution '
                                         'until 26 September 2014, of trade '
                                         'contracts concluded before 25 June '
                                         '2014, or of ancillary contracts '
                                         'necessary for the execution of such '
                                         'contracts, provided that the natural '
                                         'or legal persons, entity or body '
                                         'seeking to perform the contract have '
                                         'notified, at least 10 working days '
                                         'in advance, the activity or '
                                         'transaction to the competent '
                                         'authority of the Member State in '
                                         'which they are established. <br/>(b) '
                                         'goods originating in Crimea or '
                                         'Sevastopol which have been made '
                                         'available to the Ukrainian '
                                         'authorities for examination, for '
                                         'which compliance with the conditions '
                                         'conferring entitlement to '
                                         'preferential origin has been '
                                         'verified and for which a certificate '
                                         'of origin has been issued in '
                                         'accordance with Regulation (EU) No '
                                         '978/2012 and Regulation (EU) No '
                                         '374/2014 or in accordance with the '
                                         'EU-Ukraine Association Agreement.'}],
    'formatted_description': 'Cigars, cheroots, cigarillos and cigarettes, of '
                          'tobacco or of tobacco substitutes',
    'goods_nomenclature_item_id': '2402000000',
    'section': {'numeral': 'IV',
             'position': 4,
             'title': 'Prepared foodstuffs; beverages, spirits and vinegar; '
                      'tobacco and manufactured tobacco substitutes'}
    }
    """

import json
import logging
from datetime import datetime

from dateutil.tz import tzlocal
from django.conf import settings
from django.test import TestCase
from mixer.backend.django import mixer

from commodities.models import Commodity
from hierarchy.models import Heading, SubHeading
from trade_tariff_service.tts_api import ImportMeasureJson

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


def get_data(file_path):
    with open(file_path) as f:
        json_data = json.load(f)
    return json_data


class CommodityJsonTestCase(TestCase):
    """
    Test CommodityJson class
    """

    def setUp(self):
        self.heading = mixer.blend(
            Heading,
            heading_code=settings.TEST_HEADING_CODE,
            description=settings.TEST_HEADING_DESCRIPTION
        )
        self.subheading = mixer.blend(
            SubHeading,
            commodity_code="0101210000",
            description="Horses",
            heading=self.heading
        )
        self.commodity = mixer.blend(
            Commodity,
            commodity_code=settings.TEST_COMMODITY_CODE,
            tts_json=json.dumps(get_data(settings.COMMODITY_DATA)),
            parent_subheading=self.subheading
        )

    def test_commodity_json_repr(self):
        self.assertEqual(repr(self.commodity.tts_obj), "CommodityJson")

    def test_commodity_json_title(self):
        self.assertEqual(self.commodity.tts_obj.title, 'Pure-bred breeding animals')

    def test_commodity_heading_description(self):
        heading = self.commodity.get_heading()
        self.assertEqual(heading.description, 'Live horses, asses, mules and hinnies')

    def test_commodity_json_code(self):
        self.assertEqual(self.commodity.tts_obj.code, '0101210000')

    def test_commodity_json_chapter_note(self):
        self.maxDiff = None
        self.assertTrue(self.commodity.tts_obj.chapter_note)

    def test_commodity_chapter_title(self):
        self.assertEqual(self.commodity.tts_obj.chapter_title, 'Live animals')

    def test_commodity_section_position(self):
        self.assertEqual(self.commodity.tts_obj.section_position, 1)

    def test_commodity_duty_rate(self):
        self.assertEqual(self.commodity.tts_obj.duty_rate, 0.0)

    def test_commodity_duty_rate_with_no_match(self):
        comm_json_dict = json.loads(self.commodity.tts_json)
        comm_json_dict['basic_duty_rate'] = "<span title='0.0'>zero</span> %"
        self.commodity.tts_json = json.dumps(comm_json_dict)
        self.commodity.save()
        self.assertEqual(self.commodity.tts_obj.duty_rate, None)

    def test_commodity_get_import_measures(self):
        self.assertTrue(isinstance(self.commodity.tts_obj.get_import_measures("AF"), list))

    def test_commodity_get_import_measures_with_vat(self):
        self.assertTrue(isinstance(self.commodity.tts_obj.get_import_measures("AF", vat=True), list))

    def test_commodity_get_import_measures_with_excise(self):
        self.assertTrue(isinstance(self.commodity.tts_obj.get_import_measures("AF", excise=True), list))

    def test_commodity_get_import_measure_by_id(self):
        self.assertTrue(isinstance(self.commodity.tts_obj.get_import_measure_by_id(0, "AF"), ImportMeasureJson))

    def test_commodity_get_import_measure_by_id_that_does_not_exist(self):
        self.assertEqual(self.commodity.tts_obj.get_import_measure_by_id(10, "AF"), None)


# class CommodityHeadingJsonTestCase(TestCase):
#     """
#     Test CommodityHeadingJson class
#     """
#
#     def setUp(self):
#         self.commodity_heading = CommodityHeadingJson(get_data(settings.COMMODITYHEADINGJSON_DATA))
#
#     def test_commodity_heading_json_title(self):
#         self.assertEqual(
#             self.commodity_heading.title,
#             "Carrots, turnips, salad beetroot, salsify, celeriac, radishes and similar edible roots, fresh or chilled")
#
#     def test_commodity_heading_json_harmonized_code(self):
#         self.assertEqual(self.commodity_heading.harmonized_code, "0706000000")


# class SectionJsonTestCase(TestCase):
#     """
#     Test SectionJson class
#     """
#
#     def setUp(self):
#         self.section = SectionJson(get_data(settings.SECTIONJSON_DATA))
#
#     def test_section_json_title(self):
#         self.assertEqual(
#             self.section.title,
#             'Prepared foodstuffs; beverages, spirits and vinegar; tobacco and manufactured tobacco substitutes')
#
#     def test_section_json_chapter_ids(self):
#         self.assertEqual(self.section.chapter_ids, [16, 17, 18, 19, 20, 21, 22, 23, 24])
#
#     def test_section_json_chapter_urls(self):
#         self.assertEqual(self.section.chapter_urls,
#                          ['https://www.trade-tariff.service.gov.uk/trade-tariff/chapters/16.json',
#                           'https://www.trade-tariff.service.gov.uk/trade-tariff/chapters/17.json',
#                           'https://www.trade-tariff.service.gov.uk/trade-tariff/chapters/18.json',
#                           'https://www.trade-tariff.service.gov.uk/trade-tariff/chapters/19.json',
#                           'https://www.trade-tariff.service.gov.uk/trade-tariff/chapters/20.json',
#                           'https://www.trade-tariff.service.gov.uk/trade-tariff/chapters/21.json',
#                           'https://www.trade-tariff.service.gov.uk/trade-tariff/chapters/22.json',
#                           'https://www.trade-tariff.service.gov.uk/trade-tariff/chapters/23.json',
#                           'https://www.trade-tariff.service.gov.uk/trade-tariff/chapters/24.json'])
#
#     def test_section_json_id(self):
#         self.assertEqual(self.section.id, 4)
#
#     def test_section_json_position(self):
#         self.assertEqual(self.section.position, 4)
#
#     def test_section_json_numeral(self):
#         self.assertEqual(self.section.numeral, 'IV')


# class ChapterJsonTestCase(TestCase):
#     """
#     Test ChapterJson class
#     """
#
#     def setUp(self):
#         self.chapter = ChapterJson(get_data(settings.CHAPTERJSON_DATA))
#
#     def test_chapter_json_title(self):
#         self.assertEqual(
#             self.chapter.title,
#             'Tobacco and manufactured tobacco substitutes')
#
#     def test_chapter_harmonized_code(self):
#         self.assertEqual(
#             self.chapter.harmonized_code,
#             '2400000000')
#
#     def test_chapter_json_heading_ids(self):
#         self.assertEqual(self.chapter.heading_ids, ['2401', '2402', '2403'])
#
#     def test_chapter_json_heading_urls(self):
#         self.assertEqual(self.chapter.heading_urls,
#                          ['https://www.trade-tariff.service.gov.uk/trade-tariff/headings/2401.json',
#                           'https://www.trade-tariff.service.gov.uk/trade-tariff/headings/2402.json',
#                           'https://www.trade-tariff.service.gov.uk/trade-tariff/headings/2403.json'])


# class HeadingJsonTestCase(TestCase):
#     """
#     Test HeadingJson class
#     """
#
#     def setUp(self):
#         self.heading = HeadingJson(get_data(settings.HEADINGJSON_DATA))
#
#     def test_heading_json_title(self):
#         self.assertEqual(
#             self.heading.title,
#             'Cigars, cheroots, cigarillos and cigarettes, of tobacco or of tobacco substitutes')
#
#     def test_heading_code(self):
#         self.assertEqual(
#             self.heading.code,
#             '2402000000')
#
#     def test_heading_json_commodity_dicts(self):
#         self.assertEqual(len(self.heading.commodity_dicts), 5)
#
#     def test_heading_json_commodity_ids(self):
#         self.assertEqual(self.heading.commodity_ids, [('2402100000', True),
#                                                       ('2402200000', False),
#                                                       ('2402201000', True),
#                                                       ('2402209000', True),
#                                                       ('2402900000', True)])
#
#     def test_heading_json_commodity_ids_when_non_exists(self):
#         heading_data = get_data(settings.HEADINGJSON_DATA)
#         del heading_data['commodities']
#         updated_heading_data = HeadingJson(heading_data)
#         self.assertEqual(updated_heading_data.commodity_ids, [])
#
#     def test_heading_json_commodity_urls(self):
#         self.assertEqual(
#             self.heading.commodity_urls,
#             [(
#              'https://www.trade-tariff.service.gov.uk/trade-tariff/commodities/2402100000.json?currency=EUR&day=1&month=1&year=2019',
#              True),
#              (
#              'https://www.trade-tariff.service.gov.uk/trade-tariff/commodities/2402200000.json?currency=EUR&day=1&month=1&year=2019',
#              False),
#              (
#              'https://www.trade-tariff.service.gov.uk/trade-tariff/commodities/2402201000.json?currency=EUR&day=1&month=1&year=2019',
#              True),
#              (
#              'https://www.trade-tariff.service.gov.uk/trade-tariff/commodities/2402209000.json?currency=EUR&day=1&month=1&year=2019',
#              True),
#              (
#              'https://www.trade-tariff.service.gov.uk/trade-tariff/commodities/2402900000.json?currency=EUR&day=1&month=1&year=2019',
#              True)
#              ])
#
#     def test_heading_json_commodity_urls_when_non_exists(self):
#         heading_data = get_data(settings.HEADINGJSON_DATA)
#         del heading_data['commodities']
#         updated_heading_data = HeadingJson(heading_data)
#         self.assertEqual(updated_heading_data.commodity_urls, [])


class ImportMeasureJsonTestCase(TestCase):
    """
    Test ImportMaasureJson class
    """

    def setUp(self):
        logger.info(settings.IMPORTMEASUREJSON_DATA)
        logger.info(get_data(settings.IMPORTMEASUREJSON_DATA))
        self.import_measure = ImportMeasureJson(get_data(settings.IMPORTMEASUREJSON_DATA), settings.TEST_COMMODITY_CODE)

    def test_repr(self):
        self.assertEqual(repr(self.import_measure), "ImportMeasureJson {0} {1}".format("0101210000", "VTS"))

    def test_get_date_when_exists(self):
        self.assertTrue(isinstance(self.import_measure.get_date(
            self.import_measure.di, 'effective_start_date'), datetime))

    def test_get_date_when_none(self):
        self.assertFalse(self.import_measure.get_date(self.import_measure.di, 'effective_end_date'))

    def test_is_import(self):
        self.assertEqual(self.import_measure.is_import, True)
        self.assertTrue(isinstance(self.import_measure.is_import, bool))

    def test_origin(self):
        self.assertEqual(self.import_measure.origin, 'uk')
        self.assertTrue(isinstance(self.import_measure.origin, str))

    def test_effective_start_date(self):
        self.assertEqual(self.import_measure.effective_start_date,
                         datetime(2015, 2, 1, 0, 0, tzinfo=tzlocal()))

    def test_effective_end_date(self):
        self.assertEqual(self.import_measure.effective_end_date, None)

    def test_geographical_area(self):
        self.assertEqual(self.import_measure.geographical_area, 'ERGA OMNES')
        self.assertTrue(isinstance(self.import_measure.geographical_area, str))

    def test_geographical_area_without_erga_omnes(self):
        json_data = get_data(settings.IMPORTMEASUREJSON_DATA)
        json_data['geographical_area']['description'] = ''
        import_measure = ImportMeasureJson(json_data, settings.TEST_COMMODITY_CODE)
        self.assertEqual(import_measure.geographical_area, None)

    def test_type_id(self):
        self.assertEqual(self.import_measure.type_id, "VTS")
        self.assertTrue(isinstance(self.import_measure.type_id, str))

    def test_type_description(self):
        self.assertEqual(self.import_measure.type_description, 'VAT standard rate')
        self.assertTrue(isinstance(self.import_measure.type_description, str))

    def test_measure_id(self):
        self.assertEqual(self.import_measure.measure_id, 0)
        self.assertTrue(isinstance(self.import_measure.measure_id, int))

    def test_conditions_summary(self):
        self.assertTrue(isinstance(self.import_measure.conditions_summary, list))

    def test_excluded_country_area_ids(self):
        self.assertTrue(isinstance(self.import_measure.excluded_country_area_ids, list))

    def test_vat(self):
        self.assertTrue(self.import_measure.vat)
        self.assertTrue(isinstance(self.import_measure.vat, bool))

    def test_excise(self):
        self.assertFalse(self.import_measure.excise)
        self.assertTrue(isinstance(self.import_measure.excise, bool))

    def test_order_number_definition_summary_with_definistion(self):
        json_data = get_data(settings.IMPORTMEASUREJSON_DATA)
        json_data['order_number'] = {'definition': {'status': 'xyz'}}
        json_data['order_number']['definition']['description'] = "lipsuLorem ipsum dolor sit amet"
        import_measure = ImportMeasureJson(json_data, settings.TEST_COMMODITY_CODE)
        self.assertTrue(isinstance(import_measure.order_number_definition_summary, tuple))
        self.assertEqual(import_measure.order_number_definition_summary, ('xyz', "lipsuLorem ipsum dolor sit amet"))

    def test_order_number_definition_summary_when_none(self):
        self.assertEqual(self.import_measure.order_number_definition_summary, None)

    def test_num_conditions(self):
        self.assertEqual(self.import_measure.num_conditions, 0)
        self.assertTrue(isinstance(self.import_measure.num_conditions, int))

    def test_is_relevant_for_origin_country(self):
        self.assertEqual(self.import_measure.is_relevant_for_origin_country('AF'), True)
        self.assertTrue(isinstance(self.import_measure.is_relevant_for_origin_country('AF'), bool))

    def test_vue__legal_base_html(self):
        self.assertEqual(self.import_measure.vue__legal_base_html, '-')
        self.assertTrue(isinstance(self.import_measure.vue__legal_base_html, str))

    def test_vue__conditions_html(self):
        self.assertEqual(self.import_measure.vue__conditions_html, '-')
        self.assertTrue(isinstance(self.import_measure.vue__conditions_html, str))

    def test_vue__footnotes_html(self):
        self.assertEqual(self.import_measure.vue__footnotes_html, '<a href="#">03020</a>')
        self.assertTrue(isinstance(self.import_measure.vue__footnotes_html, str))

    def test_get_table_dict(self):
        self.assertEqual(self.import_measure.get_table_dict(), {'country': 'ERGA OMNES',
                                                                'measure_description': 'VAT standard rate',
                                                                'conditions_html': '-',
                                                                'measure_value': '20.00 %',
                                                                'excluded_countries': '',
                                                                'start_end_date': '2015-02-01',
                                                                'legal_base_html': '-',
                                                                'footnotes_html': '<a href="#">03020</a>'})
        self.assertTrue(isinstance(self.import_measure.get_table_dict(), dict))

    def test_get_table_row(self):
        # self.assertTrue(isinstance(self.import_measure, list))
        self.assertEqual(self.import_measure.get_table_row(), [['Country', 'All countries'],
                                                               ['Measure type', 'VAT standard rate'],
                                                               ['Value', '20.00 %'],
                                                               ['Conditions', '-'],
                                                               ['Excluded countries', ''],
                                                               ['Date', '1&nbsp;February&nbsp;2015']])

    def test_reformat_date(self):
        data = ['All countries', 'VAT standard rate', '20.00 %', '-', '', '2015-02-01']
        self.assertEqual(self.import_measure.reformat_date(data), ['All countries',
                                                                   'VAT standard rate',
                                                                   '20.00 %', '-',
                                                                   '',
                                                                   '1&nbsp;February&nbsp;2015'])

    def test_get_rename_countries_default(self):
        data = ['ERGA OMNES', 'VAT standard rate', '20.00 %', '-', '', '2015-02-01']
        self.assertEqual(self.import_measure.rename_countries_default(data), ['All countries',
                                                                              'VAT standard rate',
                                                                              '20.00 %',
                                                                              '-',
                                                                              '',
                                                                              '2015-02-01'])

    def test_get_measure_conditions(self):
        self.assertTrue(isinstance(self.import_measure.get_measure_conditions(), list))
        self.assertEqual(self.import_measure.get_measure_conditions(), [])

    def test_get_measure_conditions_by_id(self):
        self.assertEqual(self.import_measure.get_measure_conditions_by_measure_id(1), [])
        self.assertTrue(isinstance(self.import_measure.get_measure_conditions_by_measure_id(0), list))

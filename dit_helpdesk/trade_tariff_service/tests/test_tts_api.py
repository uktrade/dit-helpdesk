import json
import logging
from datetime import datetime

from dateutil.tz import tzlocal
from django.conf import settings
from django.test import TestCase
from mixer.backend.django import mixer

from commodities.models import Commodity
from hierarchy.models import Heading, SubHeading
from hierarchy.helpers import create_nomenclature_tree
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
        self.tree = create_nomenclature_tree('UK')

        self.heading = mixer.blend(
            Heading,
            heading_code=settings.TEST_HEADING_CODE,
            description=settings.TEST_HEADING_DESCRIPTION,
            nomenclature_tree=self.tree,
        )
        self.subheading = mixer.blend(
            SubHeading,
            commodity_code="0101210000",
            description="Horses",
            heading=self.heading,
            nomenclature_tree=self.tree,
        )
        self.commodity_data = get_data(settings.COMMODITY_DATA)
        self.commodity = mixer.blend(
            Commodity,
            commodity_code=settings.TEST_COMMODITY_CODE,
            tts_json=json.dumps(self.commodity_data),
            parent_subheading=self.subheading,
            nomenclature_tree=self.tree,
        )

    def test_commodity_json_repr(self):
        self.assertEqual(repr(self.commodity.tts_obj), "CommodityJson")

    def test_commodity_json_title(self):
        self.assertEqual(self.commodity.tts_obj.title, "Pure-bred breeding animals")

    def test_commodity_heading_description(self):
        heading = self.commodity.get_heading()
        self.assertEqual(heading.description, "Live horses, asses, mules and hinnies")

    def test_commodity_json_code(self):
        self.assertEqual(self.commodity.tts_obj.code, "0101210000")

    def test_commodity_json_chapter_note(self):
        self.maxDiff = None
        self.assertTrue(self.commodity.tts_obj.chapter_note)

    def test_commodity_get_import_measures(self):
        self.assertTrue(
            isinstance(self.commodity.tts_obj.get_import_measures("AF"), list)
        )

    def test_commodity_get_import_measures_with_vat(self):
        self.assertTrue(
            isinstance(self.commodity.tts_obj.get_import_measures("AF", vat=True), list)
        )

    def test_commodity_get_import_measures_with_excise(self):
        self.assertTrue(
            isinstance(
                self.commodity.tts_obj.get_import_measures("AF", excise=True), list
            )
        )

    def test_commodity_get_import_measure_by_id(self):
        self.assertTrue(
            isinstance(
                self.commodity.tts_obj.get_import_measure_by_id(0, "AF"),
                ImportMeasureJson,
            )
        )

    def test_commodity_get_import_measure_by_id_that_does_not_exist(self):
        self.assertEqual(
            self.commodity.tts_obj.get_import_measure_by_id(10, "AF"), None
        )

    def test_footnotes(self):
        self.assertEqual(
            self.commodity.tts_obj.footnotes,
            self.commodity_data['footnotes'],
        )

    def test_footnotes_does_not_exist(self):
        commodity_data = self.commodity_data
        del commodity_data["footnotes"]
        self.commodity.tts_json = json.dumps(self.commodity_data)
        self.commodity.save()
        self.assertEqual(self.commodity.tts_obj.footnotes, [])


class ImportMeasureJsonTestCase(TestCase):
    """
    Test ImportMaasureJson class
    """

    def setUp(self):
        tree = create_nomenclature_tree('UK')
        commodity = mixer.blend(
            Commodity,
            commodity_code=settings.TEST_COMMODITY_CODE,
            tts_json=json.dumps(get_data(settings.COMMODITY_DATA)),
            nomenclature_tree=tree,
        )
        self.import_measure = ImportMeasureJson(
            commodity,
            get_data(settings.IMPORTMEASUREJSON_DATA),
            settings.TEST_COMMODITY_CODE,
            settings.TEST_COMMODITY_DESCRIPTION,
            settings.TEST_COUNTRY_CODE,
        )

    def test_repr(self):
        self.assertEqual(
            repr(self.import_measure),
            "ImportMeasureJson {0} {1}".format("0101210000", "VTS"),
        )

    def test_origin(self):
        self.assertEqual(self.import_measure.origin, "uk")
        self.assertTrue(isinstance(self.import_measure.origin, str))

    def test_type_id(self):
        self.assertEqual(self.import_measure.type_id, "VTS")
        self.assertTrue(isinstance(self.import_measure.type_id, str))

    def test_type_description(self):
        self.assertEqual(self.import_measure.type_description, "VAT standard rate")
        self.assertTrue(isinstance(self.import_measure.type_description, str))

    def test_measure_id(self):
        self.assertEqual(self.import_measure.measure_id, 0)
        self.assertTrue(isinstance(self.import_measure.measure_id, int))

    def test_excluded_country_area_ids(self):
        self.assertTrue(isinstance(self.import_measure.excluded_country_area_ids, list))

    def test_vat(self):
        self.assertTrue(self.import_measure.vat)
        self.assertTrue(isinstance(self.import_measure.vat, bool))

    def test_excise(self):
        self.assertFalse(self.import_measure.excise)
        self.assertTrue(isinstance(self.import_measure.excise, bool))

    def test_num_conditions(self):
        self.assertEqual(self.import_measure.num_conditions, 0)
        self.assertTrue(isinstance(self.import_measure.num_conditions, int))

    def test_is_relevant_for_origin_country(self):
        self.assertEqual(self.import_measure.is_relevant_for_origin_country("AF"), True)
        self.assertTrue(
            isinstance(self.import_measure.is_relevant_for_origin_country("AF"), bool)
        )

    def test_conditions_html(self):
        def get_conditions_url(*args):
            return "TEST URL"

        self.assertEqual(self.import_measure.conditions_html(get_conditions_url), "-")
        self.assertTrue(isinstance(self.import_measure.conditions_html(get_conditions_url), str))

    def test_get_table_dict(self):
        def get_quotas_url(*args):
            return "TEST QUOTAS URL"

        def get_conditions_url(*args):
            return "TEST CONDITIONS URL"

        self.assertEqual(
            self.import_measure.get_table_dict(get_quotas_url, get_conditions_url),
            {
                "country": "ERGA OMNES",
                "measure_description": "VAT standard rate",
                "conditions_html": "-",
                "measure_value": "20.00 %",
                "excluded_countries": "",
                "start_end_date": "2015-02-01",
            },
        )
        self.assertTrue(isinstance(self.import_measure.get_table_dict(get_quotas_url, get_conditions_url), dict))

    def test_get_table_row(self):
        # self.assertTrue(isinstance(self.import_measure, list))
        def get_quotas_url(*args):
            return "TEST QUOTAS URL"

        def get_conditions_url(*args):
            return "TEST CONDITIONS URL"

        self.assertEqual(
            self.import_measure.get_table_row(get_quotas_url, get_conditions_url),
            [
                ["Country", "All countries"],
                ["Measure type", "VAT standard rate"],
                ["Value", "20.00 %"],
                ["Conditions", "-"],
                ["Start date", "1&nbsp;February&nbsp;2015"],
            ],
        )

    def test_reformat_date(self):
        data = ["All countries", "VAT standard rate", "20.00 %", "-", "", "2015-02-01"]
        self.assertEqual(
            self.import_measure.reformat_date(data),
            [
                "All countries",
                "VAT standard rate",
                "20.00 %",
                "-",
                "",
                "1&nbsp;February&nbsp;2015",
            ],
        )

    def test_get_rename_countries_default(self):
        data = ["ERGA OMNES", "VAT standard rate", "20.00 %", "-", "", "2015-02-01"]
        self.assertEqual(
            self.import_measure.rename_countries_default(data),
            ["All countries", "VAT standard rate", "20.00 %", "-", "", "2015-02-01"],
        )

    def test_get_measure_conditions(self):
        self.assertTrue(isinstance(self.import_measure.get_measure_conditions(), list))
        self.assertEqual(self.import_measure.get_measure_conditions(), [])

    def test_get_measure_conditions_by_id(self):
        self.assertEqual(
            self.import_measure.get_measure_conditions_by_measure_id(1), []
        )
        self.assertTrue(
            isinstance(
                self.import_measure.get_measure_conditions_by_measure_id(0), list
            )
        )

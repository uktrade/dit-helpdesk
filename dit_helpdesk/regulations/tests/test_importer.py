import logging

from django.conf import settings
from django.test import TestCase
from pandas import DataFrame

from commodities.models import Commodity
from regulations.importer import RegulationsImporter, data_loader
from trade_tariff_service.importer import HierarchyBuilder

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class RegulationsImporterTestCase(TestCase):

    def test_for_missing_regulations(self):
        model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]
        builder = HierarchyBuilder()
        builder.data_scanner(model_names)

        data_path = settings.REGULATIONS_DATA_PATH

        importer = RegulationsImporter()
        importer.load(data_path)
        importer.process()

        commodity_code_list = ["2621100000", "2621900000", "2703000000"]
        commodities = Commodity.objects.filter(commodity_code__in=commodity_code_list)

        regulation_title = "Voluntary - Eco-label for growing media, soil improvers and mulch"

        for item in commodities:
            logger.info(regulation_title)
            logger.info([regulation.title for regulation in item.get_regulations()])
            self.assertIn(regulation_title, [regulation.title for regulation in item.get_regulations()])

        commodity_code_list = ["9401300000", "9401590000"]
        commodities = Commodity.objects.filter(commodity_code__in=commodity_code_list)

        regulation_title = "Voluntary - Eco-label for furniture"

        for item in commodities:
            logger.info(regulation_title)
            logger.info([regulation.title for regulation in item.get_regulations()])
            self.assertIn(regulation_title, [regulation.title for regulation in item.get_regulations()])

        commodity_code_list = ["9619007100"]
        commodities = Commodity.objects.filter(commodity_code__in=commodity_code_list)

        regulation_title = "Voluntary - Eco-label for absorbent hygiene products"

        for item in commodities:
            logger.info(regulation_title)
            logger.info([regulation.title for regulation in item.get_regulations()])
            self.assertIn(regulation_title, [regulation.title for regulation in item.get_regulations()])

        commodity_code_list = ["3922100000", "4001100000", "4002410000", "4407229900", "4407913100"]
        commodities = Commodity.objects.filter(commodity_code__in=commodity_code_list)
        regulation_title = "Voluntary - Eco-label for sanitary tapware"

        for item in commodities:
            logger.info(regulation_title)
            logger.info([regulation.title for regulation in item.get_regulations()])
            # self.assertIn(regulation_title, [regulation.title for regulation in item.get_regulations()])

        commodity_code_list = ["7102310000"]
        commodities = Commodity.objects.filter(commodity_code__in=commodity_code_list)
        regulation_title = "Import restrictions for rough diamonds (Kimberley Scheme)"

        for item in commodities:
            logger.info(regulation_title)
            logger.info([regulation.title for regulation in item.get_regulations()])
            self.assertIn(regulation_title, [regulation.title for regulation in item.get_regulations()])

        commodity_code_list = ["3602000000", "3603004000", "8486100000"]
        commodities = Commodity.objects.filter(commodity_code__in=commodity_code_list)
        regulation_title = "Import requirements for firearms and warlike material"

        for item in commodities:
            logger.info(regulation_title)
            logger.info([regulation.title for regulation in item.get_regulations()])
            self.assertIn(regulation_title, [regulation.title for regulation in item.get_regulations()])

    def test_data_loader_with_csv(self):
        file_path = settings.REGULATIONS_DATA_PATH.format('product_specific_regulations.csv')
        data = data_loader(file_path)
        self.assertTrue(isinstance(data, DataFrame))

    def test_data_loader_with_json(self):
        file_path = settings.REGULATIONS_DATA_PATH.format('urls_with_text_description.json')
        data = data_loader(file_path)
        self.assertTrue(isinstance(data, dict))

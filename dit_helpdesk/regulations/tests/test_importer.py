import logging

from mixer.backend.django import mixer

from django.conf import settings
from django.test import override_settings, TestCase
from pandas import DataFrame

from commodities.models import Commodity
from regulations.importer import RegulationsImporter, data_loader
from regulations.models import Regulation
from trade_tariff_service.HierarchyBuilder import HierarchyBuilder

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class RegulationsImporterTestCase(TestCase):
    """
    Test regulations importer
    """

    @override_settings(
        HIERARCHY_MODEL_MAP={
            "Commodity": {"file_name": "test_subsets/commodities.json", "app_name": "commodities"},
            "Chapter": {"file_name": "test_subsets/chapters.json", "app_name": "hierarchy"},
            "Heading": {"file_name": "test_subsets/headings.json", "app_name": "hierarchy"},
            "SubHeading": {"file_name": "test_subsets/sub_headings.json", "app_name": "hierarchy"},
            "Section": {"file_name": "test_subsets/sections.json", "app_name": "hierarchy"},
        },
    )
    def test_regulation_groups_attached_to_commodity_objects(self):
        model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]
        builder = HierarchyBuilder()
        builder.data_scanner(model_names)
        data_path = settings.APPS_DIR + "/regulations/tests/data/{0}"

        importer = RegulationsImporter()
        importer.load(data_path)
        importer.process()

        commodity_code_list = ["2928001000", "2902500000", "2823000010"]
        commodities = Commodity.objects.filter(commodity_code__in=commodity_code_list)
        regulation_group_title = "Voluntary - Eco-label for growing media, soil improvers and mulch"
        for item in commodities:
            self.assertIn(
                regulation_group_title,
                [regulation_group.title for regulation_group in item.regulationgroup_set.all()],
            )

        commodity_code_list = ["2901100000", "7102100000"]
        commodities = Commodity.objects.filter(commodity_code__in=commodity_code_list)
        regulation_group_title = "Voluntary - Eco-label for furniture"
        for item in commodities:
            self.assertIn(
                regulation_group_title,
                [regulation_group.title for regulation_group in item.regulationgroup_set.all()],
            )

        commodity_code_list = ["2850009000"]
        commodities = Commodity.objects.filter(commodity_code__in=commodity_code_list)
        regulation_group_title = "Voluntary - Eco-label for absorbent hygiene products"
        for item in commodities:
            self.assertIn(
                regulation_group_title,
                [regulation_group.title for regulation_group in item.regulationgroup_set.all()],
            )

    @override_settings(
        HIERARCHY_MODEL_MAP={
            "Commodity": {"file_name": "test_subsets/commodities.json", "app_name": "commodities"},
            "Chapter": {"file_name": "test_subsets/chapters.json", "app_name": "hierarchy"},
            "Heading": {"file_name": "test_subsets/headings.json", "app_name": "hierarchy"},
            "SubHeading": {"file_name": "test_subsets/sub_headings.json", "app_name": "hierarchy"},
            "Section": {"file_name": "test_subsets/sections.json", "app_name": "hierarchy"},
        },
    )
    def test_sets_celex_data(self):
        model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]
        builder = HierarchyBuilder()
        builder.data_scanner(model_names)
        data_path = settings.APPS_DIR + "/regulations/tests/data/{0}"

        importer = RegulationsImporter()
        importer.load(data_path)
        importer.process()

        mapping = [
            ("http://www.legislation.gov.uk/eudn/2014/763/contents", "CELEX32014D0763"),
            ("http://www.legislation.gov.uk/eudn/2016/1332/contents", "CELEX32016D1332"),
            ("http://www.legislation.gov.uk/eudn/2014/391/contents", "CELEX32014D0391"),
            ("http://www.legislation.gov.uk/eudn/2015/2099/contents", "CELEX32015D2099"),
            ("http://www.legislation.gov.uk/eur/2010/66/contents", "CELEX32010R0066"),
            ("http://www.legislation.gov.uk/eudn/2007/64/contents", "CELEX32007D0064"),
            ("http://www.legislation.gov.uk/eudn/2006/799/contents", "CELEX32006D0799"),
        ]

        for legislation_url, celex in mapping:
            regulation = Regulation.objects.get(url=legislation_url)
            self.assertEqual(regulation.celex, celex)
        self.assertFalse(
            Regulation.objects.filter(celex="").exists(),
        )

    @override_settings(
        HIERARCHY_MODEL_MAP={
            "Commodity": {"file_name": "test_subsets/commodities.json", "app_name": "commodities"},
            "Chapter": {"file_name": "test_subsets/chapters.json", "app_name": "hierarchy"},
            "Heading": {"file_name": "test_subsets/headings.json", "app_name": "hierarchy"},
            "SubHeading": {"file_name": "test_subsets/sub_headings.json", "app_name": "hierarchy"},
            "Section": {"file_name": "test_subsets/sections.json", "app_name": "hierarchy"},
        },
    )
    def test_updated_celex_data_saves_against_existing(self):
        model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]
        builder = HierarchyBuilder()
        builder.data_scanner(model_names)
        data_path = settings.APPS_DIR + "/regulations/tests/data/{0}"

        mapping = [
            ("http://www.legislation.gov.uk/eudn/2014/763/contents", "CELEX32014D0763"),
            ("http://www.legislation.gov.uk/eudn/2016/1332/contents", "CELEX32016D1332"),
            ("http://www.legislation.gov.uk/eudn/2014/391/contents", "CELEX32014D0391"),
            ("http://www.legislation.gov.uk/eudn/2015/2099/contents", "CELEX32015D2099"),
            ("http://www.legislation.gov.uk/eur/2010/66/contents", "CELEX32010R0066"),
            ("http://www.legislation.gov.uk/eudn/2007/64/contents", "CELEX32007D0064"),
            ("http://www.legislation.gov.uk/eudn/2006/799/contents", "CELEX32006D0799"),
        ]

        for legislation_url, _ in mapping:
            mixer.blend(Regulation, url=legislation_url, celex='')

        importer = RegulationsImporter()
        importer.load(data_path)
        importer.process()

        for legislation_url, celex in mapping:
            regulation = Regulation.objects.get(url=legislation_url)
            self.assertEqual(regulation.celex, celex)
        self.assertFalse(
            Regulation.objects.filter(celex="").exists(),
        )

    def test_data_loader_with_csv(self):
        file_path = settings.REGULATIONS_DATA_PATH.format(
            "product_specific_regulations.csv"
        )
        data = data_loader(file_path)
        self.assertTrue(isinstance(data, DataFrame))

    def test_data_loader_with_json(self):
        file_path = settings.REGULATIONS_DATA_PATH.format(
            "urls_with_text_description.json"
        )
        data = data_loader(file_path)
        self.assertTrue(isinstance(data, dict))

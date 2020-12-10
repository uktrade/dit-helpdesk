import logging
import os

from django.conf import settings
from django.test import TestCase
from mixer.backend.django import mixer

from hierarchy.models import Chapter, Heading, Section
from hierarchy.helpers import create_nomenclature_tree
from rules_of_origin.RulesOfOriginImporter import RulesOfOriginImporter
from rules_of_origin.models import (
    OldRule,
    OldRuleItem,
    OldRulesGroup,
    OldRulesGroupMember,
    OldRulesDocumentFootnote,
)
from trade_tariff_service.HierarchyBuilder import HierarchyBuilder

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class ImporterTestCase(TestCase):
    """
    Test Rules of Origin Importer
    """

    def test_load(self):
        importer = RulesOfOriginImporter()
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/Autonomous_Trade_Preferences.json"
        )
        importer.load(input_file=path, priority=1)
        self.assertEqual(len(importer.data.keys()), 97)
        logger.info(importer.rules_groups)
        self.assertTrue("AUTONOMOUS_TRADE_PREFERENCES" in importer.rules_groups.keys())
        self.assertEqual(len(importer.rules_documents.keys()), 9)
        self.assertEqual(importer.working_group_name, "AUTONOMOUS_TRADE_PREFERENCES")
        self.assertEqual(importer.current_chapter_code, None)
        self.assertEqual(importer.priority, 1)
        self.assertEqual(importer.footnotes, {})

    fixtures = ["../../countries/fixtures/countries_data.json"]

    def test_instance_builder(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/Autonomous_Trade_Preferences.json"
        )
        logger.info(os.path.isfile(path))
        logger.info(path)
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 328)
        self.assertEqual(OldRuleItem.objects.count(), 476)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 1)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_for_existing_items(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format("import/EPA_Cariforum.json")
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 438)
        self.assertEqual(OldRuleItem.objects.count(), 581)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 14)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format("import/EPA_Cariforum.json")
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 438)
        self.assertEqual(OldRuleItem.objects.count(), 581)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 14)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_for_existing_items_with_hierarchy(self):
        tree = create_nomenclature_tree('UK')

        section = mixer.blend(Section, section_id=1, nomenclature_tree=tree)

        chapters = mixer.cycle(3).blend(
            Chapter,
            chapter_code=(x for x in ["0100000000", "0200000000", "0300000000"]),
            section=section, nomenclature_tree=tree
        )

        headings = mixer.cycle(4).blend(
            Heading,
            heading_code=(
                x for x in ["0304000000", "0305000000", "0306000000", "0307000000"]
            ),
            chapter=chapters[2],
            nomenclature_tree=tree,
        )

        # model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]
        # builder = HierarchyBuilder()
        #
        # builder.data_scanner(model_names)
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format("import/EPA_Cariforum.json")
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 438)
        self.assertEqual(OldRuleItem.objects.count(), 581)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 14)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_EPA_Eastern_and_Southern_Africa(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/EPA_Eastern_and_Southern_Africa.json"
        )
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 271)
        self.assertEqual(OldRuleItem.objects.count(), 285)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 4)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_EPA_Market_Access_Regulation(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/EPA_Market_Access_Regulation.json"
        )
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 445)
        self.assertEqual(OldRuleItem.objects.count(), 573)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 4)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_EPA_pacific(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format("import/EPA_pacific.json")
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 281)
        self.assertEqual(OldRuleItem.objects.count(), 299)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 3)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_EPA_South_African_Development_Community_SADC(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/EPA_South_African_Development_Community_SADC.json"
        )
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 282)
        self.assertEqual(OldRuleItem.objects.count(), 327)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 5)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_Euro_Mediterranean_Free_Trade_Area(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/Euro-Mediterranean_Free_Trade_Area.json"
        )
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 435)
        self.assertEqual(OldRuleItem.objects.count(), 516)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 9)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_FTA_Canada(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format("import/FTA_Canada.json")
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 269)
        self.assertEqual(OldRuleItem.objects.count(), 269)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 1)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_FTA_Central_America(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/FTA_Central_America.json"
        )
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 292)
        self.assertEqual(OldRuleItem.objects.count(), 327)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 6)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_FTA_Chile_Mexico(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/FTA_Chile_-_Mexico.json"
        )
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 330)
        self.assertEqual(OldRuleItem.objects.count(), 465)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 2)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_FTA_Colombia_Ecuador_and_Peru(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/FTA_Colombia,_Ecuador_and_Peru.json"
        )
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 425)
        self.assertEqual(OldRuleItem.objects.count(), 613)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 3)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_FTA_Deep_and_Comprehensive_Trade_Agreement(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/FTA_Deep_and_Comprehensive_Trade_Agreement.json"
        )
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 271)
        self.assertEqual(OldRuleItem.objects.count(), 307)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 3)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_FTA_European_Economic_Area_EEA(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/FTA_European_Economic_Area_EEA.json"
        )
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 263)
        self.assertEqual(OldRuleItem.objects.count(), 288)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 4)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_FTA_Japan(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format("import/FTA_Japan.json")
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 194)
        self.assertEqual(OldRuleItem.objects.count(), 263)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 1)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_FTA_Singapore(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format("import/FTA_Singapore.json")
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 247)
        self.assertEqual(OldRuleItem.objects.count(), 295)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 1)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_FTA_South_Korea(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format("import/FTA_South_Korea.json")
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 340)
        self.assertEqual(OldRuleItem.objects.count(), 357)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 1)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_Generalised_System_of_Preferences(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/Generalised_System_of_Preferences.json"
        )
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 264)
        self.assertEqual(OldRuleItem.objects.count(), 311)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 59)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_GSP_Plus(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format("import/GSP_Plus.json")
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 264)
        self.assertEqual(OldRuleItem.objects.count(), 311)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 6)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_Overseas_Countries_and_Territories(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/Overseas_Countries_and_Territories.json"
        )
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 205)
        self.assertEqual(OldRuleItem.objects.count(), 211)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 22)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_Pan_Euro_Mediterranean_Convention(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/Pan-Euro-Mediterranean_Convention.json"
        )
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 267)
        self.assertEqual(OldRuleItem.objects.count(), 312)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 13)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_instance_builder_Specific_Measures_Jordan(self):
        path = settings.OLD_RULES_OF_ORIGIN_DATA_PATH.format(
            "import/Specific_Measures_-_Jordan.json"
        )
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(OldRule.objects.count(), 429)
        self.assertEqual(OldRuleItem.objects.count(), 703)
        self.assertEqual(OldRulesGroup.objects.count(), 1)
        self.assertEqual(OldRulesGroupMember.objects.count(), 1)
        self.assertEqual(OldRulesDocumentFootnote.objects.count(), 0)

    def test_normalise_commodity_code(self):
        importer = RulesOfOriginImporter()
        code = importer.normalise_commodity_code({"commodity_id": "101210000"})
        self.assertEqual(code, "0101210000")
        code = importer.normalise_commodity_code({"commodity_id": "0101210000"})
        self.assertEqual(code, "0101210000")

    def test_text_sanitiser(self):
        importer = RulesOfOriginImporter()
        test = importer.text_sanitiser("some text with one of these\uf0b7in the middle")
        self.assertEqual(test, "some text with one of these&#45;in the middle")

    def test_rename_key(self):
        importer = RulesOfOriginImporter()

        old_dict = {}
        old_key = "old_key"
        old_dict[old_key] = 1
        new_dict = importer.rename_key(old_dict, old_key, "new_key")
        self.assertTrue("new_key" in new_dict.keys())
import logging

from django.conf import settings
from django.test import TestCase
from mixer.backend.django import mixer

from hierarchy.models import Chapter, Heading, Section
from rules_of_origin.importer import RulesOfOriginImporter
from rules_of_origin.models import Rule, RulesGroup, RulesGroupMember, RulesDocumentFootnote
from trade_tariff_service.importer import HierarchyBuilder

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class ImporterTestCase(TestCase):
    """
    Test Rules of Origin Importer
    """

    def test_load(self):
        importer = RulesOfOriginImporter()
        path = settings.RULES_OF_ORIGIN_DATA_PATH.format('import/OCTS.json')
        importer.load(input_file=path, priority=1)
        self.assertEqual(len(importer.data.keys()), 94)
        self.assertTrue("OCTS" in importer.rules_groups.keys())
        self.assertEqual(len(importer.rules_documents.keys()), 9)
        self.assertEqual(importer.working_group_name, 'OCTS')
        self.assertEqual(importer.current_chapter_code, None)
        self.assertEqual(importer.priority, 1)
        self.assertEqual(importer.footnotes, {})

    fixtures = ['../../countries/fixtures/countries_data.json']

    def test_instance_builder(self):
        path = settings.RULES_OF_ORIGIN_DATA_PATH.format('import/OCTS.json')
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(len(Rule.objects.all()), 280)
        self.assertEqual(len(RulesGroup.objects.all()), 1)
        self.assertEqual(len(RulesGroupMember.objects.all()), 12)
        self.assertEqual(len(RulesDocumentFootnote.objects.all()), 0)

    def test_instance_builder_for_existing_items(self):
        path = settings.RULES_OF_ORIGIN_DATA_PATH.format('import/GSP.json')
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(len(Rule.objects.all()), 266)
        self.assertEqual(len(RulesGroup.objects.all()), 1)
        self.assertEqual(len(RulesGroupMember.objects.all()), 82)
        self.assertEqual(len(RulesDocumentFootnote.objects.all()), 11)
        path = settings.RULES_OF_ORIGIN_DATA_PATH.format('import/GSP.json')
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(len(Rule.objects.all()), 266)
        self.assertEqual(len(RulesGroup.objects.all()), 1)
        self.assertEqual(len(RulesGroupMember.objects.all()), 82)
        self.assertEqual(len(RulesDocumentFootnote.objects.all()), 11)

    def test_instance_builder_for_existing_items_with_hierarchy(self):

        section = mixer.blend(
            Section,
            section_id=1
        )

        chapters = mixer.cycle(3).blend(
            Chapter,
            chapter_code=(x for x in ["0100000000", "0200000000", "0300000000"]),
            section=section
        )

        headings = mixer.cycle(4).blend(
            Heading,
            heading_code=(x for x in ["0304000000", "0305000000", "0306000000", "0307000000"]),
            chapter=chapters[2]
        )


        # model_names = ["Section", "Chapter", "Heading", "SubHeading", "Commodity"]
        # builder = HierarchyBuilder()
        #
        # builder.data_scanner(model_names)
        path = settings.RULES_OF_ORIGIN_DATA_PATH.format('test_import/GSP.json')
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(len(Rule.objects.all()), 7)
        self.assertEqual(len(RulesGroup.objects.all()), 1)
        self.assertEqual(len(RulesGroupMember.objects.all()), 82)
        self.assertEqual(len(RulesDocumentFootnote.objects.all()), 11)

    def test_instance_builder_chile(self):
        path = settings.RULES_OF_ORIGIN_DATA_PATH.format('import/CHILE_FTA.json')
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(len(Rule.objects.all()), 576)
        self.assertEqual(len(RulesGroup.objects.all()), 1)
        self.assertEqual(len(RulesGroupMember.objects.all()), 1)
        self.assertEqual(len(RulesDocumentFootnote.objects.all()), 11)

    def test_instance_builder_EPA_ESA(self):
        path = settings.RULES_OF_ORIGIN_DATA_PATH.format('import/EPA_ESA.json')
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(len(Rule.objects.all()), 511)
        self.assertEqual(len(RulesGroup.objects.all()), 1)
        self.assertEqual(len(RulesGroupMember.objects.all()), 4)
        self.assertEqual(len(RulesDocumentFootnote.objects.all()), 10)

    def test_instance_builder_EPA_pacific(self):
        path = settings.RULES_OF_ORIGIN_DATA_PATH.format('import/EPA_pacific.json')
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(len(Rule.objects.all()), 437)
        self.assertEqual(len(RulesGroup.objects.all()), 1)
        self.assertEqual(len(RulesGroupMember.objects.all()), 2)
        self.assertEqual(len(RulesDocumentFootnote.objects.all()), 0)

    def test_instance_builder_EPA_faroe_islands(self):
        path = settings.RULES_OF_ORIGIN_DATA_PATH.format('import/PEM_faroe_islands.json')
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(len(Rule.objects.all()), 605)
        self.assertEqual(len(RulesGroup.objects.all()), 1)
        self.assertEqual(len(RulesGroupMember.objects.all()), 1)
        self.assertEqual(len(RulesDocumentFootnote.objects.all()), 11)

    def test_instance_builder_EPA_Israel(self):
        path = settings.RULES_OF_ORIGIN_DATA_PATH.format('import/PEM_Israel.json')
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(len(Rule.objects.all()), 578)
        self.assertEqual(len(RulesGroup.objects.all()), 1)
        self.assertEqual(len(RulesGroupMember.objects.all()), 1)
        self.assertEqual(len(RulesDocumentFootnote.objects.all()), 11)

    def test_instance_builder_EPA_palestine(self):
        path = settings.RULES_OF_ORIGIN_DATA_PATH.format('import/PEM_palestine.json')
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(len(Rule.objects.all()), 605)
        self.assertEqual(len(RulesGroup.objects.all()), 1)
        self.assertEqual(len(RulesGroupMember.objects.all()), 1)
        self.assertEqual(len(RulesDocumentFootnote.objects.all()), 11)

    def test_instance_builder_PEM_switzerland_liechtenstein(self):
        path = settings.RULES_OF_ORIGIN_DATA_PATH.format('import/PEM_switzerland_&_liechtenstein.json')
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(len(Rule.objects.all()), 605)
        self.assertEqual(len(RulesGroup.objects.all()), 1)
        self.assertEqual(len(RulesGroupMember.objects.all()), 2)
        self.assertEqual(len(RulesDocumentFootnote.objects.all()), 11)

    def test_instance_builder_EEA(self):
        path = settings.RULES_OF_ORIGIN_DATA_PATH.format('import/EEA.json')
        importer = RulesOfOriginImporter()
        importer.load(input_file=path, priority=1)
        importer.instance_builder()
        self.assertEqual(len(Rule.objects.all()), 0)
        self.assertEqual(len(RulesGroup.objects.all()), 1)
        self.assertEqual(len(RulesGroupMember.objects.all()), 0)
        self.assertEqual(len(RulesDocumentFootnote.objects.all()), 0)

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
        new_dict = importer.rename_key(old_dict,  old_key, "new_key")
        self.assertTrue("new_key" in new_dict.keys())

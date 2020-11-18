import logging
import os

from django.conf import settings
from django.test import TestCase, override_settings
from django.core.management import call_command

from mixer.backend.django import mixer

from hierarchy.models import Chapter, Heading
from hierarchy.helpers import create_nomenclature_tree
from countries.models import Country
from rules_of_origin.models import (
    RulesDocument,
    Rule,
    SubRule,
    RulesDocumentFootnote,
)
from rules_of_origin.ingest.importer import InvalidDocumentException


logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


apps_dir = settings.APPS_DIR
test_data_path = os.path.join(
    apps_dir, 'rules_of_origin', 'data', 'test_import', 'SAMPLE_FTA.xml'
)


def _just10(val):
    return val.ljust(10)


@override_settings(RULES_OF_ORIGIN_DATA_PATH=test_data_path)
class ImporterTestCase(TestCase):
    """
    Test Rules of Origin Importer
    """

    def setUp(self):
        self.country = mixer.blend(Country, name='Test Country', country_code='TC')

        self.tree = create_nomenclature_tree()

        for model_class in (Chapter, Heading):
            mixer.register(model_class, nomenclature_tree=self.tree)

        self.chapter1 = mixer.blend(Chapter, chapter_code=_just10('01'))

        self.chapter4 = mixer.blend(Chapter, chapter_code=_just10('04'))
        self.heading0403 = mixer.blend(
            Heading,
            heading_code=_just10('0403'),
            heading_code_4='0403',
            chapter=self.chapter4
        )

        self.chapter13 = mixer.blend(Chapter, chapter_code=_just10('13'))
        self.heading1302 = mixer.blend(
            Heading,
            heading_code=_just10('1302'),
            heading_code_4='1302',
        )

        start_code_int = 1507
        mixer.cycle(9).blend(
            Heading,
            heading_code=(_just10(str(start_code_int + inc)) for inc in range(9)),
            heading_code_4=(str(start_code_int + inc) for inc in range(9)),
        )

    def test_import_roo(self):
        call_command('import_rules_of_origin')

        self.assertEqual(RulesDocument.objects.count(), 1)
        self.assertEqual(Rule.objects.count(), 5)
        self.assertEqual(SubRule.objects.count(), 5)
        self.assertEqual(RulesDocumentFootnote.objects.count(), 12)

        rules_document = RulesDocument.objects.first()
        self.assertIn(self.country, rules_document.countries.all())

        rule1 = self.chapter1.rules_of_origin.first()
        self.assertEqual(rule1.description, 'Live animals')
        self.assertFalse(rule1.is_exclusion)
        self.assertFalse(rule1.subrule_set.exists())

        rule4 = self.chapter4.rules_of_origin.first()
        self.assertTrue(rule4.is_exclusion)

        rule0403 = self.heading0403.rules_of_origin.first()
        self.assertFalse(rule0403.is_exclusion)

        rule_multiple = Rule.objects.get(code='1507 to 1515')
        self.assertEqual(rule_multiple.headings.count(), 9)

    def test_import_roo__invalid_country(self):
        Country.objects.all().delete()

        with self.assertRaises(InvalidDocumentException):
            call_command('import_rules_of_origin')

        self.assertFalse(RulesDocument.objects.exists())
        self.assertFalse(Rule.objects.exists())
        self.assertFalse(SubRule.objects.exists())
        self.assertFalse(RulesDocumentFootnote.objects.exists())

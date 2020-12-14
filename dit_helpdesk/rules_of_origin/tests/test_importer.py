import logging
import os
import datetime as dt

from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings
from django.core.management import call_command

from mixer.backend.django import mixer

from freezegun import freeze_time

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
    return val.ljust(10, '0')


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
        self.chapter15 = mixer.blend(Chapter, chapter_code=_just10('15'))
        mixer.cycle(9).blend(
            Heading,
            heading_code=(_just10(str(start_code_int + inc)) for inc in range(9)),
            heading_code_4=(str(start_code_int + inc) for inc in range(9)),
            chapter=self.chapter15,
        )

    def test_import_roo(self):
        call_command('import_rules_of_origin')

        self.assertEqual(RulesDocument.objects.count(), 1)
        self.assertEqual(Rule.objects.count(), 6)
        self.assertEqual(SubRule.objects.count(), 5)
        self.assertEqual(RulesDocumentFootnote.objects.count(), 12)

        rules_document = RulesDocument.objects.first()
        self.assertIn(self.country, rules_document.countries.all())

        rule1 = self.chapter1.rules_of_origin.first()
        self.assertEqual(rule1.description, 'Live animals')
        self.assertFalse(rule1.is_exclusion)
        self.assertFalse(rule1.subrules.exists())

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

    @freeze_time('2020-12-30')
    def test_get_rules__pre_start_date(self):
        call_command('import_rules_of_origin')

        h1509 = Heading.objects.get(heading_code_4='1509')

        with mock.patch('hierarchy.models.Heading.get_hierarchy_context_ids') as mock_context_ids:
            mock_context_ids.return_value = self.chapter15.id, h1509.id, None
            roo_data = h1509.get_rules_of_origin(
                country_code='TC', starting_before=dt.datetime.now())

        self.assertFalse(roo_data)

    @freeze_time('2021-01-01')
    def test_get_rules__post_start_date(self):
        call_command('import_rules_of_origin')

        h1509 = Heading.objects.get(heading_code_4='1509')

        with mock.patch('hierarchy.models.Heading.get_hierarchy_context_ids') as mock_context_ids:
            mock_context_ids.return_value = self.chapter15.id, h1509.id, None
            roo_data = h1509.get_rules_of_origin(country_code='TC')

        self.assertTrue(roo_data)

    @freeze_time('2021-01-01')
    def test_ex_inheritance(self):
        call_command('import_rules_of_origin')

        h1509 = Heading.objects.get(heading_code_4='1509')

        with mock.patch('hierarchy.models.Heading.get_hierarchy_context_ids') as mock_context_ids:
            mock_context_ids.return_value = self.chapter15.id, h1509.id, None
            roo_data = h1509.get_rules_of_origin(country_code='TC')

        roo_data = roo_data['FTA Test Country']

        rules = roo_data['rules']
        # confirm that an 'ex Chapter' is not returned as a rule
        self.assertEquals(len(rules), 1)

        rule = rules[0]
        self.assertTrue(rule.headings.exists())
        self.assertFalse(rule.is_exclusion)
        self.assertFalse(rule.chapters.exists())

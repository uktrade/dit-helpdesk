import logging
import datetime as dt

from unittest import mock

from django.test import TestCase, override_settings
from django.core.management import call_command

from mixer.backend.django import Mixer

from hierarchy.models import Chapter, Heading
from hierarchy.helpers import create_nomenclature_tree
from countries.models import Country
from rules_of_origin.models import RulesDocument, Rule, SubRule, RulesDocumentFootnote

from rules_of_origin.ingest.importer import (
    InvalidDocumentException,
    RulesDocumentAlreadyExistsException,
)


logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


def _just10(val):
    return val.ljust(10, "0")


@override_settings(
    ROO_S3_SECRET_ACCESS_KEY="minio_password",  # pragma: allowlist secret
    ROO_S3_ACCESS_KEY_ID="minio_username",
    ROO_S3_BUCKET_NAME="test-bucket-roo-import-success",
)
class ImporterTestCase(TestCase):
    """
    Test Rules of Origin Importer
    """

    def setUp(self):
        mixer = Mixer()

        self.country = mixer.blend(
            Country,
            name="Test Country",
            country_code="XT",
            trade_agreement_title="The White-Gold Concordat",
        )

        self.tree = create_nomenclature_tree()

        for model_class in (Chapter, Heading):
            mixer.register(model_class, nomenclature_tree=self.tree)

        self.chapter1 = mixer.blend(Chapter, chapter_code=_just10("01"))

        self.chapter4 = mixer.blend(Chapter, chapter_code=_just10("04"))
        self.heading0403 = mixer.blend(
            Heading,
            heading_code=_just10("0403"),
            heading_code_4="0403",
            chapter=self.chapter4,
        )

        self.chapter13 = mixer.blend(Chapter, chapter_code=_just10("13"))
        self.heading1302 = mixer.blend(
            Heading, heading_code=_just10("1302"), heading_code_4="1302"
        )

        start_code_int = 1507
        self.chapter15 = mixer.blend(Chapter, chapter_code=_just10("15"))
        mixer.cycle(9).blend(
            Heading,
            heading_code=(_just10(str(start_code_int + inc)) for inc in range(9)),
            heading_code_4=(str(start_code_int + inc) for inc in range(9)),
            chapter=self.chapter15,
        )

    def test_import_roo(self):
        call_command("import_rules_of_origin")

        self.assertEqual(RulesDocument.objects.count(), 1)
        self.assertEqual(Rule.objects.count(), 6)
        self.assertEqual(SubRule.objects.count(), 5)
        self.assertEqual(RulesDocumentFootnote.objects.count(), 12)

        rules_document = RulesDocument.objects.first()
        self.assertIn(self.country, rules_document.countries.all())
        self.assertEqual(rules_document.description, self.country.trade_agreement_title)

        rule1 = self.chapter1.rules_of_origin.first()
        self.assertEqual(rule1.description, "Live animals")
        self.assertFalse(rule1.is_exclusion)
        self.assertFalse(rule1.subrules.exists())

        rule4 = self.chapter4.rules_of_origin.first()
        self.assertTrue(rule4.is_exclusion)

        rule0403 = self.heading0403.rules_of_origin.first()
        self.assertFalse(rule0403.is_exclusion)

        rule_multiple = Rule.objects.get(code="1507 to 1515")
        self.assertEqual(rule_multiple.headings.count(), 9)

    def test_import_roo_invalid_country(self):
        Country.objects.all().delete()

        with self.assertRaises(InvalidDocumentException):
            call_command("import_rules_of_origin")

        self.assertFalse(RulesDocument.objects.exists())
        self.assertFalse(Rule.objects.exists())
        self.assertFalse(SubRule.objects.exists())
        self.assertFalse(RulesDocumentFootnote.objects.exists())

    @override_settings(ROO_S3_BUCKET_NAME="test-bucket-roo-import-future-start-date")
    def test_get_rules_pre_start_date(self):
        call_command("import_rules_of_origin")

        h1509 = Heading.objects.get(heading_code_4="1509")

        with mock.patch(
            "hierarchy.models.Heading.get_hierarchy_context_ids"
        ) as mock_context_ids:
            mock_context_ids.return_value = (self.chapter15.id, h1509.id, None, None)
            roo_data = h1509.get_rules_of_origin(
                country_code=self.country.country_code,
                starting_before=dt.datetime.now(),
            )

        self.assertFalse(roo_data)

    def test_get_rules_post_start_date(self):
        call_command("import_rules_of_origin")

        h1509 = Heading.objects.get(heading_code_4="1509")

        with mock.patch(
            "hierarchy.models.Heading.get_hierarchy_context_ids"
        ) as mock_context_ids:
            mock_context_ids.return_value = (self.chapter15.id, h1509.id, None, None)
            roo_data = h1509.get_rules_of_origin(country_code=self.country.country_code)

        self.assertTrue(roo_data)

    def test_ex_inheritance(self):
        call_command("import_rules_of_origin")

        h1509 = Heading.objects.get(heading_code_4="1509")

        with mock.patch(
            "hierarchy.models.Heading.get_hierarchy_context_ids"
        ) as mock_context_ids:
            mock_context_ids.return_value = (self.chapter15.id, h1509.id, None, None)
            roo_data = h1509.get_rules_of_origin(country_code=self.country.country_code)

        roo_data = roo_data[self.country.trade_agreement_title]

        # confirm that the name to display on the frontend matches the trade agreement name
        self.assertEquals(roo_data["rule_doc_name"], self.country.trade_agreement_title)

        rules = roo_data["rules"]
        # confirm that an 'ex Chapter' is not returned as a rule
        self.assertEquals(len(rules), 1)

        rule = rules[0]
        self.assertTrue(rule.headings.exists())
        self.assertFalse(rule.is_exclusion)
        self.assertFalse(rule.chapters.exists())

    @override_settings(ROO_S3_BUCKET_NAME="test-bucket-roo-import-duplicates")
    def test_duplicate_country_found(self):
        with self.assertRaises(
            RulesDocumentAlreadyExistsException
        ) as duplicate_exception, self.assertLogs(
            "rules_of_origin.management.commands.import_rules_of_origin", level="ERROR"
        ) as error_log:
            call_command("import_rules_of_origin")

        exception_msg = str(duplicate_exception.exception)
        self.assertEqual(
            exception_msg,
            "RulesDocument has already been created for country_code XT \n"
            "during this operation, check your source folder for duplicate XMLs or errors.",
        )
        self.assertEqual(
            duplicate_exception.exception.country,
            self.country,
        )
        self.assertEqual(
            error_log[0][0].getMessage(),
            f"Failed to import rules_of_origin/SAMPLE_FTA_DUPLICATE.xml. Found duplicate country {self.country}. "
            "Already created from rules_of_origin/SAMPLE_FTA.xml",
        )

    @override_settings(
        SUPPORTED_TRADE_SCENARIOS=["TEST_TA"],
        SCENARIOS_WITH_UK_TRADE_AGREEMENT=["TEST_TA"],
        MULTIPLE_ROO_SCENARIOS=["TEST_TA"],
        ROO_S3_BUCKET_NAME="test-bucket-roo-import-duplicates",
    )
    def test_import_multiple_roo(self):
        self.country.scenario = "TEST_TA"
        self.country.save()

        call_command("import_rules_of_origin")

        self.assertEqual(RulesDocument.objects.count(), 2)
        self.assertEqual(Rule.objects.count(), 12)
        self.assertEqual(SubRule.objects.count(), 10)
        self.assertEqual(RulesDocumentFootnote.objects.count(), 24)

        rules_documents = RulesDocument.objects.all()
        for doc in rules_documents:
            self.assertIn(self.country, doc.countries.all())

        # Next section ensures the RoO section on the frontend will replace the
        # trade agreement name with the GSP title
        h1509 = Heading.objects.get(heading_code_4="1509")

        with mock.patch(
            "hierarchy.models.Heading.get_hierarchy_context_ids"
        ) as mock_context_ids:
            mock_context_ids.return_value = (self.chapter15.id, h1509.id, None, None)
            roo_data = h1509.get_rules_of_origin(country_code=self.country.country_code)

        # Ensure that when there is a TA and a GSP rule doc, the TA one is first in the ordereddict
        for count, value in enumerate(roo_data):
            if count == 0:
                self.assertEquals(
                    roo_data[value]["rule_doc_name"], self.country.trade_agreement_title
                )
            elif count == 1:
                self.assertEquals(
                    roo_data[value]["rule_doc_name"],
                    "Generalised Scheme of Preferences",
                )
            print(count, value)

    @override_settings(ROO_S3_BUCKET_NAME="test-bucket-roo-import-empty")
    def test_no_files_in_s3_bucket(self):
        with self.assertRaises(Exception) as empty_exception:
            call_command("import_rules_of_origin")

        exception_msg = str(empty_exception.exception)
        self.assertEqual(
            exception_msg,
            "No Rules of Origin files in s3 Bucket",
        )

    @override_settings(ROO_S3_BUCKET_NAME="test-bucket-roo-import-missing-prefix")
    def test_no_roo_prefix_in_s3_bucket(self):
        with self.assertRaises(Exception) as empty_exception:
            call_command("import_rules_of_origin")

        exception_msg = str(empty_exception.exception)
        self.assertEqual(
            exception_msg,
            "No Rules of Origin files in s3 Bucket",
        )

    @override_settings(ROO_S3_BUCKET_NAME="test-bucket-roo-import-alt-country-code")
    def test_alternative_country_code(self):
        self.country.alternative_non_trade_country_code = "XA"
        self.country.save()

        call_command("import_rules_of_origin")

        self.assertEqual(RulesDocument.objects.count(), 1)
        self.assertEqual(Rule.objects.count(), 6)
        self.assertEqual(SubRule.objects.count(), 5)
        self.assertEqual(RulesDocumentFootnote.objects.count(), 12)

        rules_document = RulesDocument.objects.first()
        self.assertIn(self.country, rules_document.countries.all())

        rule1 = self.chapter1.rules_of_origin.first()
        self.assertEqual(rule1.description, "Live animals")
        self.assertFalse(rule1.is_exclusion)
        self.assertFalse(rule1.subrules.exists())

        rule4 = self.chapter4.rules_of_origin.first()
        self.assertTrue(rule4.is_exclusion)

        rule0403 = self.heading0403.rules_of_origin.first()
        self.assertFalse(rule0403.is_exclusion)

        rule_multiple = Rule.objects.get(code="1507 to 1515")
        self.assertEqual(rule_multiple.headings.count(), 9)

    @override_settings(
        SUPPORTED_TRADE_SCENARIOS=["TEST_TA"],
        SCENARIOS_WITH_UK_TRADE_AGREEMENT=["TEST_TA", "ANDORRA"],
    )
    def test_check_countries_consistency_via_importer(self):
        self.country.scenario = "TEST_TA"
        self.country.save()

        with self.assertLogs(
            "rules_of_origin.ingest.importer", level="ERROR"
        ) as warning_log:
            call_command("import_rules_of_origin")

        # Assert 'XT - Test Country' is not in the error message to sentry
        self.assertNotIn("XT - Test Country", str(warning_log.output))

    @override_settings(SCENARIOS_WITH_UK_TRADE_AGREEMENT=["TEST_TA"])
    def test_check_countries_consistency_via_command(self):
        mixer = Mixer()
        country_missing_roo = mixer.blend(
            Country,
            name="Test Country 2",
            country_code="BX",
            scenario="TEST_TA",
        )
        country_missing_roo.save()

        with self.assertLogs(
            "rules_of_origin.ingest.importer", level="ERROR"
        ) as warning_log:
            call_command("check_rules_of_origin")

        # Assert 'BX - Test Country 2' is in the error message to sentry
        self.assertIn("BX - Test Country 2", str(warning_log.output))

    @override_settings(ROO_S3_BUCKET_NAME="test-bucket-roo-import-gsp")
    def test_import_roo_gsp_country(self):
        mixer = Mixer()
        country_ldc = mixer.blend(
            Country,
            name="Test Country 2",
            country_code="BX",
            scenario="TEST_TA",
        )
        country_ldc.save()

        call_command("import_rules_of_origin")

        ldc_rules_document = RulesDocument.objects.get(countries=country_ldc)
        self.assertEqual(
            ldc_rules_document.description, "Generalised Scheme of Preferences"
        )

        obc_rules_document = RulesDocument.objects.get(countries=self.country)
        self.assertEqual(
            obc_rules_document.description, "Generalised Scheme of Preferences"
        )

        # Next section ensures the RoO section on the frontend will replace a non-existent
        # trade agreement name with the GSP title
        h1509 = Heading.objects.get(heading_code_4="1509")

        with mock.patch(
            "hierarchy.models.Heading.get_hierarchy_context_ids"
        ) as mock_context_ids:
            mock_context_ids.return_value = (self.chapter15.id, h1509.id, None, None)
            roo_data_ldc = h1509.get_rules_of_origin(
                country_code=country_ldc.country_code
            )
            roo_data_obc = h1509.get_rules_of_origin(
                country_code=self.country.country_code
            )

        roo_data_ldc = roo_data_ldc["Generalised Scheme of Preferences"]
        self.assertEquals(
            roo_data_ldc["rule_doc_name"], "Generalised Scheme of Preferences"
        )

        roo_data_obc = roo_data_obc["Generalised Scheme of Preferences"]
        self.assertEquals(
            roo_data_obc["rule_doc_name"], "Generalised Scheme of Preferences"
        )

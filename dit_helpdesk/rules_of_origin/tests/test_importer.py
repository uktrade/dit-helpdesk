import logging

from django.test import TestCase, override_settings
from django.core.management import call_command

from mixer.backend.django import Mixer

from commodities.models import Commodity
from countries.models import Country
from rules_of_origin.hierarchy import get_rules_of_origin
from rules_of_origin.ingest.importer import (
    InvalidDocumentException,
    RulesDocumentAlreadyExistsException,
)
from rules_of_origin.models import RulesDocument, Rule, SubRule, RulesDocumentFootnote


logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


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

        self.gsp_country = mixer.blend(
            Country,
            name="Test Country 2",
            country_code="BX",
            scenario="TEST_TA",
        )

        self.commodity = mixer.blend(Commodity, commodity_code="0100000000")

    def test_import_roo(self):
        # Test that running import_rules_of_origin from SAMPLE_FTA.xml will populate
        # the Rule and RuleDocument DB tables, and that they relate to each other correctly
        call_command("import_rules_of_origin")

        # Should be one rule document, with the correct trade agreement name and country
        self.assertEqual(RulesDocument.objects.count(), 1)
        rules_document = RulesDocument.objects.first()
        self.assertIn(self.country, rules_document.countries.all())
        self.assertEqual(rules_document.description, self.country.trade_agreement_title)

        # Should be 6 rules all linked to the rule document object
        self.assertEqual(Rule.objects.count(), 6)
        rules = Rule.objects.filter(rules_document=rules_document)
        self.assertEqual(rules.count(), 6)

        # Should be 5 subrules linked to the rules - rule 1302 contains 2 and 1507 to 1515 contains 3
        self.assertEqual(SubRule.objects.count(), 5)
        subrule_counts = {}
        for rule in rules:
            subrules = SubRule.objects.filter(rule=rule)
            subrule_counts[rule.code] = subrules.count()
        self.assertEqual(subrule_counts["ex Chapter 15"], 0)
        self.assertEqual(subrule_counts["0403"], 0)
        self.assertEqual(subrule_counts["Chapter 01"], 0)
        self.assertEqual(subrule_counts["ex Chapter 04"], 0)
        self.assertEqual(subrule_counts["1302"], 2)
        self.assertEqual(subrule_counts["1507 to 1515"], 3)

        # Should be 12 footnotes all linked to the rules document
        self.assertEqual(RulesDocumentFootnote.objects.count(), 12)
        footnotes = RulesDocumentFootnote.objects.filter(rules_document=rules_document)
        self.assertEqual(footnotes.count(), 12)

    def test_import_roo_invalid_country(self):
        # Test outcome when SAMPLE_FTA.xml is for a country that doesn't exist
        # We expect an error to be thrown and no rules to be added to the DB
        Country.objects.all().delete()

        with self.assertRaises(InvalidDocumentException):
            call_command("import_rules_of_origin")

        self.assertFalse(RulesDocument.objects.exists())
        self.assertFalse(Rule.objects.exists())
        self.assertFalse(SubRule.objects.exists())
        self.assertFalse(RulesDocumentFootnote.objects.exists())

    @override_settings(ROO_S3_BUCKET_NAME="test-bucket-roo-import-future-start-date")
    def test_get_rules_pre_start_date(self):
        # Test to ensure any SAMPLE_FTA.xml indicating a start date in the future
        # results in those rules not being returned when calling the get_rules_of_origin function
        call_command("import_rules_of_origin")

        roo_data = get_rules_of_origin(
            country_code=self.country.country_code,
            commodity_code=self.commodity.commodity_code,
        )

        self.assertFalse(roo_data)
        # Due to the date in the sample file, this test will fail in the year 2500
        # Happy New Year, future developer person.

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
        # Test to ensure that GSP countries will have rules added to the DB for both their
        # trade agreement and according to the GSP
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

        roo_data = get_rules_of_origin(
            country_code=self.country.country_code,
            commodity_code=self.commodity.commodity_code,
        )

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
        # Test to ensure a country code in SAMPLE_FTA.xml which is a countrys alternative
        # code is still processed and its rules added to the DB
        self.country.alternative_non_trade_country_code = "XA"
        self.country.save()

        call_command("import_rules_of_origin")

        # Should be one rule document, with the correct trade agreement name and country
        self.assertEqual(RulesDocument.objects.count(), 1)
        rules_document = RulesDocument.objects.first()
        self.assertIn(self.country, rules_document.countries.all())
        self.assertEqual(rules_document.description, self.country.trade_agreement_title)

        # Should be 6 rules all linked to the rule document object
        self.assertEqual(Rule.objects.count(), 6)
        rules = Rule.objects.filter(rules_document=rules_document)
        self.assertEqual(rules.count(), 6)

        # Should be 5 subrules linked to the rules - rule 1302 contains 2 and 1507 to 1515 contains 3
        self.assertEqual(SubRule.objects.count(), 5)
        subrule_counts = {}
        for rule in rules:
            subrules = SubRule.objects.filter(rule=rule)
            subrule_counts[rule.code] = subrules.count()
        self.assertEqual(subrule_counts["ex Chapter 15"], 0)
        self.assertEqual(subrule_counts["0403"], 0)
        self.assertEqual(subrule_counts["Chapter 01"], 0)
        self.assertEqual(subrule_counts["ex Chapter 04"], 0)
        self.assertEqual(subrule_counts["1302"], 2)
        self.assertEqual(subrule_counts["1507 to 1515"], 3)

        # Should be 12 footnotes all linked to the rules document
        self.assertEqual(RulesDocumentFootnote.objects.count(), 12)
        footnotes = RulesDocumentFootnote.objects.filter(rules_document=rules_document)
        self.assertEqual(footnotes.count(), 12)

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
        # Test to ensure rules are added for countries in GSP status from files marked LDC and OBC
        # (Least Developed Countries and Other Beneficiary Countries)
        call_command("import_rules_of_origin")

        ldc_rules_document = RulesDocument.objects.get(countries=self.gsp_country)
        self.assertEqual(
            ldc_rules_document.description, "Generalised Scheme of Preferences"
        )

        obc_rules_document = RulesDocument.objects.get(countries=self.country)
        self.assertEqual(
            obc_rules_document.description, "Generalised Scheme of Preferences"
        )

        roo_data_ldc = get_rules_of_origin(
            country_code=self.gsp_country.country_code,
            commodity_code=self.commodity.commodity_code,
        )

        roo_data_obc = get_rules_of_origin(
            country_code=self.country.country_code,
            commodity_code=self.commodity.commodity_code,
        )

        roo_data_ldc = roo_data_ldc["Generalised Scheme of Preferences"]
        self.assertEquals(
            roo_data_ldc["rule_doc_name"], "Generalised Scheme of Preferences"
        )

        roo_data_obc = roo_data_obc["Generalised Scheme of Preferences"]
        self.assertEquals(
            roo_data_obc["rule_doc_name"], "Generalised Scheme of Preferences"
        )

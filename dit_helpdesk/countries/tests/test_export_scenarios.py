import csv
import os

from io import StringIO

from django.test import TestCase
from unittest.mock import patch
from django.core.management import call_command

from countries.models import Country

from mixer.backend.django import Mixer

import logging

logger = logging.getLogger(__name__)


class ExportScenariosTestCase(TestCase):

    """
    CSV Exporter tests
    """

    def setUp(self):
        Country.objects.all().delete()

        mixer = Mixer()

        self.country = mixer.blend(
            Country,
            name="Test Country",
            country_code="XT",
            has_eu_trade_agreement=False,
            scenario="STICKER_TRADES",
            content_url="gotgotgotneed.com",
            trade_agreement_title="The Very Agreeable Agreement",
            trade_agreement_type="Football Sticker Swap",
        )
        self.country.save()

    def test_export_scenarios_csv(self):
        call_command("export_scenarios", "--output=unit_test_csv.csv")
        test_csv_file = "/app/unit_test_csv.csv"

        # Expect a CSV file output, format will be a list for each line
        expected_fields = [
            "country_code",
            "country_name",
            "uk_agreement_status",
            "eu_agreement_status",
            "scenario",
            "govuk_fta_url",
            "trade_agreement_title",
            "trade_agreement_type",
        ]

        expected_row = [
            "XT",
            "Test Country",
            "False",
            "False",
            "STICKER_TRADES",
            "gotgotgotneed.com",
            "The Very Agreeable Agreement",
            "Football Sticker Swap",
        ]

        with open(test_csv_file, "r") as file:
            reader = csv.reader(file)
            country_csv_headers = next(reader)
            self.assertListEqual(country_csv_headers, expected_fields)
            country_csv_content = next(reader)
            self.assertListEqual(country_csv_content, expected_row)

        os.remove(test_csv_file)

    def test_export_scenarios_stdout(self):

        # Expect a log in string form, 2 lines listing information without spaces
        expected_log = (
            "country_code,country_name,uk_agreement_status,eu_agreement_status,"
            "scenario,govuk_fta_url,trade_agreement_title,trade_agreement_type\r\n"
            "XT,Test Country,False,False,STICKER_TRADES,gotgotgotneed.com,"
            "The Very Agreeable Agreement,Football Sticker Swap\r\n"
        )

        with patch("sys.stdout", new=StringIO()) as output:
            call_command("export_scenarios")
            log_content = output.getvalue()
            self.assertEqual(log_content, expected_log)

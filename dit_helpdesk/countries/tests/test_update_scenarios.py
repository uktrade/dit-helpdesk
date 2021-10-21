import requests_mock

from io import StringIO
from unittest import mock

from mixer.backend.django import mixer

from django.core.management import call_command
from django.test import TestCase

from rules_of_origin.models import RulesDocument

from ..models import Country
from ..scenarios import ALL_GSP_IDS, GSP_GENERAL_ID, GSP_ENHANCED_ID, update_scenario


class UpdateScenarioTestCase(TestCase):
    def test_no_transition(self):
        country = mixer.blend(Country, scenario="MADE_UP")

        update_scenario(country)

        self.assertEqual(country.scenario, "MADE_UP")

    def test_trade_agreement_no_roo_to_trade_agreement(self):
        country = mixer.blend(Country, scenario="TRADE_AGREEMENT_NO_ROO_TWUK")

        update_scenario(country)
        self.assertEqual(country.scenario, "TRADE_AGREEMENT_NO_ROO_TWUK")

        mixer.blend(RulesDocument, countries=country)
        update_scenario(country)
        self.assertEqual(country.scenario, "TRADE_AGREEMENT")

    @requests_mock.Mocker()
    def test_dom_leg_gsp_with_exclusions_to_gsp(self, mocked_requests):
        country = mixer.blend(Country, scenario="DOM_LEG_GSP_WITH_EXCLUSIONS")

        mocked_requests.get(
            "https://www.trade-tariff.service.gov.uk/api/v2/geographical_areas",
            json={
                "data": [
                    {
                        "id": "1111",
                        "relationships": {
                            "children_geographical_areas": {
                                "data": [{"id": "1"}, {"id": "2"}],
                            },
                        },
                    },
                    {
                        "id": GSP_ENHANCED_ID,
                        "relationships": {
                            "children_geographical_areas": {
                                "data": [{"id": "1"}],
                            },
                        },
                    },
                ]
            },
        )
        update_scenario(country)
        self.assertEqual(country.scenario, "DOM_LEG_GSP_WITH_EXCLUSIONS")

        mocked_requests.get(
            "https://www.trade-tariff.service.gov.uk/api/v2/geographical_areas",
            json={
                "data": [
                    {
                        "id": "1111",
                        "relationships": {
                            "children_geographical_areas": {
                                "data": [{"id": "1"}, {"id": "2"}],
                            },
                        },
                    },
                    {
                        "id": GSP_ENHANCED_ID,
                        "relationships": {
                            "children_geographical_areas": {
                                "data": [{"id": country.country_code}],
                            },
                        },
                    },
                ]
            },
        )
        update_scenario(country)
        self.assertEqual(country.scenario, "GSP")

    @requests_mock.Mocker()
    def test_trade_agreement_gsp_trans(self, mocked_requests):
        country = mixer.blend(Country, scenario="TRADE_AGREEMENT_GSP_TRANS")

        mocked_requests.get(
            "https://www.trade-tariff.service.gov.uk/api/v2/geographical_areas",
            json={
                "data": [
                    {
                        "id": "1111",
                        "relationships": {
                            "children_geographical_areas": {
                                "data": [{"id": "1"}, {"id": "2"}],
                            },
                        },
                    },
                    {
                        "id": GSP_GENERAL_ID,
                        "relationships": {
                            "children_geographical_areas": {
                                "data": [{"id": country.country_code}],
                            },
                        },
                    },
                ]
            },
        )
        update_scenario(country)
        self.assertEqual(country.scenario, "TRADE_AGREEMENT_GSP_TRANS")

        mocked_requests.get(
            "https://www.trade-tariff.service.gov.uk/api/v2/geographical_areas",
            json={
                "data": [
                    {
                        "id": "1111",
                        "relationships": {
                            "children_geographical_areas": {
                                "data": [{"id": "1"}, {"id": "2"}],
                            },
                        },
                    },
                    {
                        "id": GSP_GENERAL_ID,
                        "relationships": {
                            "children_geographical_areas": {
                                "data": [],
                            },
                        },
                    },
                ]
            },
        )
        update_scenario(country)
        self.assertEqual(country.scenario, "TRADE_AGREEMENT")

    @requests_mock.Mocker()
    def test_gsp_to_non_pref(self, mocked_requests):
        for gsp_id in ALL_GSP_IDS:
            country = mixer.blend(Country, scenario="GSP")

            mocked_requests.get(
                "https://www.trade-tariff.service.gov.uk/api/v2/geographical_areas",
                json={
                    "data": [
                        {
                            "id": "1111",
                            "relationships": {
                                "children_geographical_areas": {
                                    "data": [{"id": "1"}, {"id": "2"}],
                                },
                            },
                        },
                        {
                            "id": gsp_id,
                            "relationships": {
                                "children_geographical_areas": {
                                    "data": [{"id": country.country_code}],
                                },
                            },
                        },
                    ]
                },
            )
            update_scenario(country)
            self.assertEqual(country.scenario, "GSP")

            mocked_requests.get(
                "https://www.trade-tariff.service.gov.uk/api/v2/geographical_areas",
                json={
                    "data": [
                        {
                            "id": "1111",
                            "relationships": {
                                "children_geographical_areas": {
                                    "data": [{"id": "1"}, {"id": "2"}],
                                },
                            },
                        },
                        {
                            "id": gsp_id,
                            "relationships": {
                                "children_geographical_areas": {
                                    "data": [{"id": "1"}],
                                },
                            },
                        },
                    ]
                },
            )
            update_scenario(country)
            self.assertEqual(country.scenario, "NON_PREF")


class UpdateScenarioManagementCommandTestCase(TestCase):
    @mock.patch("countries.management.commands.update_scenarios.update_scenario")
    def test_dry_run(self, mock_update_scenario):
        Country.objects.all().delete()

        country = mixer.blend(Country, scenario="BEFORE")

        def _update_scenario(country):
            country.scenario = "AFTER"
            country.save()

        mock_update_scenario.side_effect = _update_scenario

        out = StringIO()
        call_command("update_scenarios", "--dry-run", stdout=out)
        country.refresh_from_db()

        out.seek(0)
        self.assertEqual(
            out.readlines(),
            [
                "Would update:\n",
                f"{country.country_code}: BEFORE -> AFTER\n",
            ],
        )
        self.assertEqual(country.scenario, "BEFORE")

    @mock.patch("countries.management.commands.update_scenarios.update_scenario")
    def test_update(self, mock_update_scenario):
        Country.objects.all().delete()

        country = mixer.blend(Country, scenario="BEFORE")

        def _update_scenario(country):
            country.scenario = "AFTER"
            country.save()

        mock_update_scenario.side_effect = _update_scenario

        out = StringIO()
        call_command("update_scenarios", stdout=out)
        country.refresh_from_db()

        out.seek(0)
        self.assertEqual(
            out.readlines(),
            [
                "Updated:\n",
                f"{country.country_code}: BEFORE -> AFTER\n",
            ],
        )
        self.assertEqual(country.scenario, "AFTER")

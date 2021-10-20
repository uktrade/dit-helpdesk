import requests_mock

from mixer.backend.django import mixer

from django.test import TestCase

from rules_of_origin.models import RulesDocument

from ..models import Country
from ..scenarios import update_scenario


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
                        "id": "2027",
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
                        "id": "2027",
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
                        "id": "2020",
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
                        "id": "2020",
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

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

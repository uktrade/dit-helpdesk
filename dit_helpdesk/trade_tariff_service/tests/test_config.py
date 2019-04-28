from django.test import TestCase
from django.apps import apps
from trade_tariff_service.apps import TradeTariffServiceConfig


class TradeTariffServiceConfigTestCase(TestCase):

    def test_apps(self):
        self.assertEqual(TradeTariffServiceConfig.name,'trade_tariff_service')
        self.assertEqual(apps.get_app_config('trade_tariff_service').name, 'trade_tariff_service')
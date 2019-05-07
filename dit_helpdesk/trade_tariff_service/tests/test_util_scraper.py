import json

from django.conf import settings
from django.test import TestCase

from trade_tariff_service.util_scraper import get_commodity_json


class UtilScraperTestCase(TestCase):
    def test_get_commodity_json(self):
        resp = get_commodity_json(settings.TEST_COMMODITY_CODE)
        self.assertEqual(json.loads(resp)['goods_nomenclature_item_id'], settings.TEST_COMMODITY_CODE)

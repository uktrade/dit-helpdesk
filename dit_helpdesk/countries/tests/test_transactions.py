import logging
from django.conf import settings
from django.test import TestCase

from countries.models import Country

logger = logging.getLogger(__name__)
# logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class CountryFixturesTestCase(TestCase):

    """
    Country Fixtures tests
    """

    fixtures = [settings.COUNTRIES_DATA + '/countries/fixtures/countries_data.json']

    def test_fixtures_load_countries_data(self):
        self.assertTrue(Country.objects.count() > 0)

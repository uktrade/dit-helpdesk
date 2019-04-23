from django.test import TestCase
from model_mommy import mommy
import logging
logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.DEBUG)


class RegulationTestCase(TestCase):

    def setUp(self):
        self.regulation = mommy.make('Regulation')

    def test_str(self):
        self.assertEquals(str(self.regulation), self.regulation.title)


class DocumentTestCase(TestCase):

    def setUp(self):
        self.document = mommy.make('Document')

    def test_str(self):
        self.assertEquals(self.document.__str__(), self.document.url)


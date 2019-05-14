from mixer.backend.django import mixer
from django.test import TestCase
from model_mommy import mommy
import logging

from regulations.models import Regulation, Document

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class RegulationTestCase(TestCase):
    """
    Test regulation model
    """

    def setUp(self):
        self.regulation = mixer.blend(Regulation)

    def test_str(self):
        self.assertEquals(str(self.regulation), self.regulation.title)


class DocumentTestCase(TestCase):
    """
    Test Document model
    """

    def setUp(self):
        self.document = mixer.blend(Document)

    def test_str(self):
        self.assertEquals(self.document.__str__(), self.document.url)

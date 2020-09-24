from mixer.backend.django import mixer
from django.test import TestCase
from model_mommy import mommy
import logging

from regulations.models import RegulationGroup, Regulation

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class RegulationGroupTestCase(TestCase):
    """
    Test regulation model
    """

    def setUp(self):
        self.regulation = mixer.blend(RegulationGroup)

    def test_str(self):
        self.assertEquals(str(self.regulation), self.regulation.title)


class RegulationTestCase(TestCase):
    """
    Test Regulation model
    """

    def setUp(self):
        self.regulation = mixer.blend(Regulation)

    def test_str(self):
        self.assertEquals(self.regulation.__str__(), self.regulation.url)

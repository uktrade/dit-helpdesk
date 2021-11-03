import logging

from django.test import TestCase
from mixer.backend.django import mixer

from rules_of_origin.models import RulesDocument, RulesDocumentFootnote, Rule

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class RulesDocumentCase(TestCase):
    """
    Test Rules Document model
    """

    def setUp(self):
        self.rulesdocument = mixer.blend(RulesDocument)

    def test_str(self):
        self.assertEquals(str(self.rulesdocument), self.rulesdocument.description)


class RuleTestCase(TestCase):
    """
    Test Rule model
    """

    def setUp(self):
        self.rule = mixer.blend(Rule, description="test description")

    def test_str(self):
        self.assertEquals(str(self.rule), self.rule.description)


class RulesDocumentFootnoteTestCase(TestCase):
    """
    Test Rules Document Footnote model
    """

    def setUp(self):
        self.rulesdocumentfootnote = mixer.blend(RulesDocumentFootnote)

    def test_str(self):
        self.assertEquals(
            str(self.rulesdocumentfootnote),
            "Footnote {0}".format(self.rulesdocumentfootnote.number),
        )

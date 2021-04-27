import logging

from django.test import TestCase
from model_mommy import mommy

from rules_of_origin.models import RulesDocument, RulesDocumentFootnote, Rule

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class RulesDocumentCase(TestCase):
    """
    Test Rules Document model
    """

    def setUp(self):
        self.rulesdocument = mommy.make(RulesDocument)

    def test_str(self):
        self.assertEquals(str(self.rulesdocument), self.rulesdocument.description)


class RuleTestCase(TestCase):
    """
    Test Rule model
    """

    def setUp(self):
        self.rule = mommy.make(Rule, description="test description")

    def test_str(self):
        self.assertEquals(str(self.rule), self.rule.description)


class RulesDocumentFootnoteTestCase(TestCase):
    """
    Test Rules Document Footnote model
    """

    def setUp(self):
        self.rulesdocumentfootnote = mommy.make(RulesDocumentFootnote)

    def test_str(self):
        self.assertEquals(
            str(self.rulesdocumentfootnote),
            "Footnote {0}".format(self.rulesdocumentfootnote.number),
        )

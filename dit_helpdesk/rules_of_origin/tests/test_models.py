import logging

from django.test import TestCase
from mixer.backend.django import mixer

from rules_of_origin.models import RulesDocument, RulesDocumentFootnote, Rule

logger = logging.getLogger(__name__)


class RulesDocumentCase(TestCase):
    """
    Test Rules Document model
    """

    def test_str(self):
        rules_document = mixer.blend(
            RulesDocument,
            description="DESCRIPTION",
        )

        self.assertEquals(
            str(rules_document),
            "DESCRIPTION",
        )


class RuleTestCase(TestCase):
    """
    Test Rule model
    """

    def test_str(self):
        rules_document = mixer.blend(
            RulesDocument, description="RULES DOCUMENT DESCRIPTION"
        )
        rule = mixer.blend(
            Rule,
            code="RULE CODE",
            rules_document=rules_document,
        )

        self.assertEquals(
            str(rule),
            "RULES DOCUMENT DESCRIPTION - RULE CODE",
        )


class RulesDocumentFootnoteTestCase(TestCase):
    """
    Test Rules Document Footnote model
    """

    def test_str(self):
        rulesdocumentfootnote = mixer.blend(
            RulesDocumentFootnote,
            number=1,
        )

        self.assertEquals(str(rulesdocumentfootnote), "Footnote 1")

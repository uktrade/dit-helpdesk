import logging

from django.test import TestCase
from model_mommy import mommy

from rules_of_origin.models import (
    OldRulesGroup, OldRulesGroupMember, OldRulesDocument, OldRulesDocumentFootnote,
    OldRule,
)

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class RulesGroupTestCase(TestCase):
    """
    Test Rules Group model
    """

    def setUp(self):
        self.rulesgroup = mommy.make(OldRulesGroup)

    def test_str(self):
        self.assertEquals(str(self.rulesgroup), self.rulesgroup.description)


class RulesGroupMemberTestCase(TestCase):
    """
    Test Rules Group Member model
    """

    def setUp(self):
        self.rulesgroupmember = mommy.make(OldRulesGroupMember)

    def test_str(self):
        test_str = "{1} Old rules group member {0}".format(
            self.rulesgroupmember.country.country_code,
            self.rulesgroupmember.old_rules_group.description,
        )
        self.assertEquals(str(self.rulesgroupmember), test_str)

    def test_rule_group_member_has_start_date(self):
        self.assertTrue(self.rulesgroupmember.start_date)


class RulesDocumentCase(TestCase):
    """
    Test Rules Document model
    """

    def setUp(self):
        self.rulesdocument = mommy.make(OldRulesDocument)

    def test_str(self):
        self.assertEquals(str(self.rulesdocument), self.rulesdocument.description)


class RuleTestCase(TestCase):
    """
    Test Rule model
    """

    def setUp(self):
        self.rule = mommy.make(OldRule)

    def test_str(self):
        self.assertEquals(str(self.rule), self.rule.rule_id)


class RulesDocumentFootnoteTestCase(TestCase):
    """
    Test Rules Document Footnote model
    """

    def setUp(self):
        self.rulesdocumentfootnote = mommy.make(OldRulesDocumentFootnote)

    def test_str(self):
        self.assertEquals(
            str(self.rulesdocumentfootnote),
            "Footnote {0}".format(self.rulesdocumentfootnote.number),
        )

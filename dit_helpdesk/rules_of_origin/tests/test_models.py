import logging

from django.test import TestCase
from model_mommy import mommy

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class RulesGroupTestCase(TestCase):
    """
    Test Rules Group model
    """

    def setUp(self):
        self.rulesgroup = mommy.make("RulesGroup")

    def test_str(self):
        self.assertEquals(str(self.rulesgroup), self.rulesgroup.description)


class RulesGroupMemberTestCase(TestCase):
    """
    Test Rules Group Member model
    """

    def setUp(self):
        self.rulesgroupmember = mommy.make("RulesGroupMember")

    def test_str(self):
        test_str = "{1} Rules group member {0}".format(
            self.rulesgroupmember.country.country_code,
            self.rulesgroupmember.rules_group.description,
        )
        self.assertEquals(str(self.rulesgroupmember), test_str)

    def test_rule_group_member_has_start_date(self):
        self.assertTrue(self.rulesgroupmember.start_date)


class RulesDocumentCase(TestCase):
    """
    Test Rules Document model
    """

    def setUp(self):
        self.rulesdocument = mommy.make("RulesDocument")

    def test_str(self):
        self.assertEquals(str(self.rulesdocument), self.rulesdocument.description)


class RuleTestCase(TestCase):
    """
    Test Rule model
    """

    def setUp(self):
        self.rule = mommy.make("Rule")

    def test_str(self):
        self.assertEquals(str(self.rule), self.rule.description)


class RulesDocumentFootnoteTestCase(TestCase):
    """
    Test Rules Document Footnote model
    """

    def setUp(self):
        self.rulesdocumentfootnote = mommy.make("RulesDocumentFootnote")

    def test_str(self):
        self.assertEquals(
            str(self.rulesdocumentfootnote),
            "Footnote {0}".format(self.rulesdocumentfootnote.number),
        )

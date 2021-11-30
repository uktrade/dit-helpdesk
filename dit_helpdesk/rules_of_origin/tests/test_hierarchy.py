import logging

from django.test import TestCase
from mixer.backend.django import mixer

from rules_of_origin.models import RulesDocument, Rule

from rules_of_origin.hierarchy import get_rules_of_origin


logger = logging.getLogger(__name__)


class GetRulesOfOriginTestCase(TestCase):
    """
    Test the get_rules_of_origin function
    coverage run manage.py test dit_helpdesk/rules_of_origin/tests/test_hierarchy.py --settings=config.settings.test
    """

    def test_no_rules_in_rules_document(self):
        rules_document = mixer.blend(RulesDocument)

        rules_of_origin = get_rules_of_origin(rules_document, "01")

        self.assertCountEqual(rules_of_origin, [])

    def test_rules_directly_applied_to_commodity_code(self):
        rules_document = mixer.blend(RulesDocument)
        rule_01 = mixer.blend(
            Rule,
            hs_from="01",
            hs_to=None,
            rules_document=rules_document,
        )
        rule_02 = mixer.blend(
            Rule,
            hs_from="02",
            hs_to=None,
            rules_document=rules_document,
        )
        rule_03 = mixer.blend(
            Rule,
            hs_from="03",
            hs_to=None,
            rules_document=rules_document,
        )
        another_rule_03 = mixer.blend(
            Rule,
            hs_from="03",
            hs_to=None,
            rules_document=rules_document,
        )

        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [rule_01])

        rules_of_origin = get_rules_of_origin(rules_document, "02")
        self.assertCountEqual(rules_of_origin, [rule_02])

        rules_of_origin = get_rules_of_origin(rules_document, "03")
        self.assertCountEqual(rules_of_origin, [another_rule_03, rule_03])

        rules_of_origin = get_rules_of_origin(rules_document, "04")
        self.assertCountEqual(rules_of_origin, [])

    def test_rules_in_hierarchy_for_commodity_code(self):
        rules_document = mixer.blend(RulesDocument)

        rule = mixer.blend(
            Rule,
            hs_from="01",
            hs_to=None,
            rules_document=rules_document,
        )
        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0102")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "010203")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "01020304")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0102030405")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "010203040506")
        self.assertCountEqual(rules_of_origin, [rule])

        rule.hs_from = "0102"
        rule.save()
        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [])
        rules_of_origin = get_rules_of_origin(rules_document, "0102")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "010203")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "01020304")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0102030405")
        self.assertCountEqual(rules_of_origin, [rule])

        rule.hs_from = "010203"
        rule.save()
        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [])
        rules_of_origin = get_rules_of_origin(rules_document, "0102")
        self.assertCountEqual(rules_of_origin, [])
        rules_of_origin = get_rules_of_origin(rules_document, "010203")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "01020304")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0102030405")
        self.assertCountEqual(rules_of_origin, [rule])

        another_rule = mixer.blend(
            Rule,
            hs_from="0102",
            hs_to=None,
            rules_document=rules_document,
        )
        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [])
        rules_of_origin = get_rules_of_origin(rules_document, "0102")
        self.assertCountEqual(rules_of_origin, [another_rule])
        # rules_of_origin = get_rules_of_origin(rules_document, "010203")
        # self.assertCountEqual(rules_of_origin, [rule, another_rule])
        # rules_of_origin = get_rules_of_origin(rules_document, "01020304")
        # self.assertCountEqual(rules_of_origin, [rule, another_rule])
        # rules_of_origin = get_rules_of_origin(rules_document, "0102030405")
        # self.assertCountEqual(rules_of_origin, [rule, another_rule])

    def test_ranged_rules_for_commodity_code(self):
        rules_document = mixer.blend(RulesDocument)

        rule = mixer.blend(
            Rule,
            hs_from="01",
            hs_to="02",
            rules_document=rules_document,
        )
        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0102")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "010203")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "01020304")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0102030405")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "010203040506")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "02")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0203")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "020304")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "02030405")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0203040506")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "020304050607")
        self.assertCountEqual(rules_of_origin, [rule])

        rule.hs_from = "0102"
        rule.hs_to = "02"
        rule.save()
        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [])
        rules_of_origin = get_rules_of_origin(rules_document, "0101")
        self.assertCountEqual(rules_of_origin, [])
        rules_of_origin = get_rules_of_origin(rules_document, "0102")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "010203")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "01020304")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0102030405")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "010203040506")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "02")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0203")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "020304")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "02030405")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0203040506")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "020304050607")
        self.assertCountEqual(rules_of_origin, [rule])

        rule.hs_from = "01"
        rule.hs_to = "0203"
        rule.save()
        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0102")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "02")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0203")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "020304")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "02030405")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0203040506")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "020304050607")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0204")
        self.assertCountEqual(rules_of_origin, [])
        rules_of_origin = get_rules_of_origin(rules_document, "0205")
        self.assertCountEqual(rules_of_origin, [])

        rule.hs_from = "010203"
        rule.hs_to = "020304"
        rule.save()
        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [])
        rules_of_origin = get_rules_of_origin(rules_document, "0102")
        self.assertCountEqual(rules_of_origin, [])
        rules_of_origin = get_rules_of_origin(rules_document, "010202")
        self.assertCountEqual(rules_of_origin, [])
        rules_of_origin = get_rules_of_origin(rules_document, "010203")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "010204")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "02")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "020304")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "020305")
        self.assertCountEqual(rules_of_origin, [])
        rules_of_origin = get_rules_of_origin(rules_document, "0204")
        self.assertCountEqual(rules_of_origin, [])
        rules_of_origin = get_rules_of_origin(rules_document, "0205")
        self.assertCountEqual(rules_of_origin, [])

        rule.hs_from = "01"
        rule.hs_to = "0203"
        rule.save()
        another_rule = mixer.blend(
            Rule,
            hs_from="02",
            hs_to="0304",
            rules_document=rules_document,
        )
        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0102")
        self.assertCountEqual(rules_of_origin, [rule])
        # rules_of_origin = get_rules_of_origin(rules_document, "02")
        # self.assertCountEqual(rules_of_origin, [rule, another_rule])
        # rules_of_origin = get_rules_of_origin(rules_document, "020304")
        # self.assertCountEqual(rules_of_origin, [rule, another_rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0204")
        self.assertCountEqual(rules_of_origin, [another_rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0205")
        self.assertCountEqual(rules_of_origin, [another_rule])
        rules_of_origin = get_rules_of_origin(rules_document, "03")
        self.assertCountEqual(rules_of_origin, [another_rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0304")
        self.assertCountEqual(rules_of_origin, [another_rule])
        rules_of_origin = get_rules_of_origin(rules_document, "0305")
        self.assertCountEqual(rules_of_origin, [])
        rules_of_origin = get_rules_of_origin(rules_document, "04")
        self.assertCountEqual(rules_of_origin, [])

    def test_non_ex_rules_override_parent_rules(self):
        rules_document = mixer.blend(RulesDocument)

        chapter_rule = mixer.blend(
            Rule,
            hs_from="01",
            hs_to=None,
            rules_document=rules_document,
        )
        heading_rule = mixer.blend(
            Rule,
            hs_from="0101",
            hs_to=None,
            rules_document=rules_document,
        )
        subheading_rule = mixer.blend(
            Rule,
            hs_from="010101",
            hs_to=None,
            rules_document=rules_document,
        )

        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [chapter_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "0101")
        self.assertCountEqual(rules_of_origin, [heading_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "010101")
        self.assertCountEqual(rules_of_origin, [subheading_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "01010101")
        self.assertCountEqual(rules_of_origin, [subheading_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "0101010101")
        self.assertCountEqual(rules_of_origin, [subheading_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "010101010101")
        self.assertCountEqual(rules_of_origin, [subheading_rule])

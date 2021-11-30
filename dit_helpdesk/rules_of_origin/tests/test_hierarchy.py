import logging

from django.test import TestCase
from mixer.backend.django import mixer

from rules_of_origin.models import Rule, RulesDocument, RulesDocumentFootnote

from rules_of_origin.hierarchy import get_rules_of_origin, process_footnotes


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

    def test_non_ex_rules_directly_applied_to_commodity_code(self):
        rules_document = mixer.blend(RulesDocument)
        rule_01 = mixer.blend(
            Rule,
            hs_from="01",
            hs_to=None,
            is_extract=False,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )
        rule_02 = mixer.blend(
            Rule,
            hs_from="02",
            hs_to=None,
            is_extract=False,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )
        rule_03 = mixer.blend(
            Rule,
            hs_from="03",
            hs_to=None,
            is_extract=False,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )
        another_rule_03 = mixer.blend(
            Rule,
            hs_from="03",
            hs_to=None,
            is_extract=False,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )

        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [rule_01])

        rules_of_origin = get_rules_of_origin(rules_document, "02")
        self.assertCountEqual(rules_of_origin, [rule_02])

        rules_of_origin = get_rules_of_origin(rules_document, "03")
        self.assertCountEqual(rules_of_origin, [another_rule_03, rule_03])

        rules_of_origin = get_rules_of_origin(rules_document, "04")
        self.assertCountEqual(rules_of_origin, [])

    def test_non_ex_rules_in_hierarchy_for_commodity_code(self):
        rules_document = mixer.blend(RulesDocument)

        rule = mixer.blend(
            Rule,
            hs_from="01",
            hs_to=None,
            is_exlusion=False,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
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

    def test_non_ex_ranged_rules_for_commodity_code(self):
        rules_document = mixer.blend(RulesDocument)

        rule = mixer.blend(
            Rule,
            hs_from="01",
            hs_to="02",
            is_extract=False,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
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

    def test_non_ex_rules_override_parent_rules(self):
        rules_document = mixer.blend(RulesDocument)

        chapter_rule = mixer.blend(
            Rule,
            hs_from="01",
            hs_to=None,
            is_extract=False,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )
        heading_rule = mixer.blend(
            Rule,
            hs_from="0101",
            hs_to=None,
            is_extract=False,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )
        subheading_rule = mixer.blend(
            Rule,
            hs_from="010101",
            hs_to=None,
            is_extract=False,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
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

    def test_non_ex_rule_with_leading_rule(self):
        # A leading rule is one without `rule_text`
        rules_document = mixer.blend(RulesDocument)

        chapter_rule = mixer.blend(
            Rule,
            code="chapter_rule",
            hs_from="01",
            hs_to=None,
            is_extract=False,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )
        heading_leading_rule = mixer.blend(
            Rule,
            code="heading_leading_rule",
            hs_from="0101",
            hs_to=None,
            is_extract=False,
            rules_document=rules_document,
            rule_text=None,
        )
        subheading_rule = mixer.blend(
            Rule,
            code="subheading_rule",
            hs_from="010101",
            hs_to=None,
            is_extract=False,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )

        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [chapter_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "0101")
        self.assertCountEqual(rules_of_origin, [heading_leading_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "010101")
        self.assertCountEqual(rules_of_origin, [heading_leading_rule, subheading_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "01010101")
        self.assertCountEqual(rules_of_origin, [heading_leading_rule, subheading_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "0101010101")
        self.assertCountEqual(rules_of_origin, [heading_leading_rule, subheading_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "010101010101")
        self.assertCountEqual(rules_of_origin, [heading_leading_rule, subheading_rule])

    def test_ex_rules_directly_applied_overlap(self):
        rules_document = mixer.blend(RulesDocument)

        chapter_rule = mixer.blend(
            Rule,
            code="chapter_rule",
            hs_from="01",
            hs_to=None,
            is_extract=True,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )
        heading_rule = mixer.blend(
            Rule,
            code="heading_rule",
            hs_from="0101",
            hs_to=None,
            is_extract=True,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )
        subheading_rule = mixer.blend(
            Rule,
            code="subheading_rule",
            hs_from="010101",
            hs_to=None,
            is_extract=True,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )

        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [chapter_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "0101")
        self.assertCountEqual(rules_of_origin, [chapter_rule, heading_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "010101")
        self.assertCountEqual(
            rules_of_origin, [chapter_rule, heading_rule, subheading_rule]
        )

        rules_of_origin = get_rules_of_origin(rules_document, "01010101")
        self.assertCountEqual(
            rules_of_origin, [chapter_rule, heading_rule, subheading_rule]
        )

        rules_of_origin = get_rules_of_origin(rules_document, "0101010101")
        self.assertCountEqual(
            rules_of_origin, [chapter_rule, heading_rule, subheading_rule]
        )

        rules_of_origin = get_rules_of_origin(rules_document, "010101010101")
        self.assertCountEqual(
            rules_of_origin, [chapter_rule, heading_rule, subheading_rule]
        )

        other_chapter_rule = mixer.blend(
            Rule,
            code="other_chapter_rule",
            hs_from="01",
            hs_to=None,
            is_extract=True,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )

        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [chapter_rule, other_chapter_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "0101")
        self.assertCountEqual(
            rules_of_origin, [other_chapter_rule, chapter_rule, heading_rule]
        )

    def test_ex_rules_ranged_overlap(self):
        rules_document = mixer.blend(RulesDocument)

        chapter_rule = mixer.blend(
            Rule,
            code="chapter_rule",
            hs_from="01",
            hs_to="02",
            is_extract=True,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )
        heading_rule = mixer.blend(
            Rule,
            code="heading_rule",
            hs_from="0105",
            hs_to="0205",
            is_extract=True,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )
        subheading_rule = mixer.blend(
            Rule,
            code="subheading_rule",
            hs_from="010505",
            hs_to="020505",
            is_extract=True,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )

        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [chapter_rule])

        rules_of_origin = get_rules_of_origin(rules_document, "02")
        self.assertCountEqual(
            rules_of_origin, [chapter_rule, heading_rule, subheading_rule]
        )

        rules_of_origin = get_rules_of_origin(rules_document, "0110")
        self.assertCountEqual(
            rules_of_origin, [chapter_rule, heading_rule, subheading_rule]
        )

        rules_of_origin = get_rules_of_origin(rules_document, "0205")
        self.assertCountEqual(
            rules_of_origin, [chapter_rule, heading_rule, subheading_rule]
        )

        rules_of_origin = get_rules_of_origin(rules_document, "020505")
        self.assertCountEqual(
            rules_of_origin, [chapter_rule, heading_rule, subheading_rule]
        )

    def test_multiple_rules_documents(self):
        rules_document = mixer.blend(RulesDocument)
        rules_document_chapter_rule = mixer.blend(
            Rule,
            hs_from="01",
            hs_to=None,
            is_extract=False,
            rules_document=rules_document,
            rule_text=mixer.RANDOM,
        )

        other_rules_document = mixer.blend(RulesDocument)
        other_rules_document_chapter_rule = mixer.blend(
            Rule,
            hs_from="01",
            hs_to=None,
            is_extract=False,
            rules_document=other_rules_document,
            rule_text=mixer.RANDOM,
        )

        rules_of_origin = get_rules_of_origin(rules_document, "01")
        self.assertCountEqual(rules_of_origin, [rules_document_chapter_rule])

        rules_of_origin = get_rules_of_origin(other_rules_document, "01")
        self.assertCountEqual(rules_of_origin, [other_rules_document_chapter_rule])


class GetRulesFootnotes(TestCase):
    def test_process_footnotes_no_footnotes(self):
        rules = Rule.objects.none()
        notes = RulesDocumentFootnote.objects.none()

        processed_footnotes = process_footnotes(rules, notes)

        self.assertEqual(processed_footnotes, [])

    def test_process_footnotes_with_footnote(self):
        rule = mixer.blend(Rule, rule_text_processed="This has a footnote [001].")
        note = mixer.blend(RulesDocumentFootnote, identifier="001")

        processed_footnotes = process_footnotes([rule], [note])

        self.assertEqual(processed_footnotes, [note])
        self.assertEqual(
            rule.rule_text_processed,
            'This has a footnote <sup><a href="#roo_note_1" class="govuk-link">1)</a></sup>.',
        )

    def test_process_footnotes_with_filtering(self):

        rule = mixer.blend(Rule, rule_text_processed="This has a footnote [002].")
        note_001 = mixer.blend(RulesDocumentFootnote, identifier="001")
        note_002 = mixer.blend(RulesDocumentFootnote, identifier="002")
        note_003 = mixer.blend(RulesDocumentFootnote, identifier="003")

        processed_footnotes = process_footnotes([rule], [note_001, note_002, note_003])

        self.assertEqual(processed_footnotes, [note_002])
        self.assertEqual(
            rule.rule_text_processed,
            'This has a footnote <sup><a href="#roo_note_1" class="govuk-link">1)</a></sup>.',
        )

    def test_process_footnotes_alphabetical_notes(self):
        rule = mixer.blend(Rule, rule_text_processed="This has a footnote [a].")
        note = mixer.blend(RulesDocumentFootnote, identifier="001")

        processed_footnotes = process_footnotes([rule], [note])

        self.assertEqual(processed_footnotes, [note])
        self.assertEqual(
            rule.rule_text_processed,
            'This has a footnote <sup><a href="#roo_note_1" class="govuk-link">1)</a></sup>.',
        )

    def test_process_footnotes_alphabetical_notes_filtered(self):
        rule = mixer.blend(Rule, rule_text_processed="This has a footnote [b].")
        note_001 = mixer.blend(RulesDocumentFootnote, identifier="001")
        note_002 = mixer.blend(RulesDocumentFootnote, identifier="002")
        note_003 = mixer.blend(RulesDocumentFootnote, identifier="003")

        processed_footnotes = process_footnotes([rule], [note_001, note_002, note_003])

        self.assertEqual(processed_footnotes, [note_002])
        self.assertEqual(
            rule.rule_text_processed,
            'This has a footnote <sup><a href="#roo_note_1" class="govuk-link">1)</a></sup>.',
        )

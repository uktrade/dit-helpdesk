from django.test import TestCase

from mixer.backend.django import Mixer

from rules_of_origin.models import Rule, RulesDocumentFootnote

from ..helpers import create_nomenclature_tree
from ..models import Chapter
from .models import RulesOfOriginMixinModel


class RulesOfOriginMixinTestCase(TestCase):
    def setUp(self):
        tree = create_nomenclature_tree("UK")

        self.roo_mixer = Mixer()

        self.roo_mixer.register(Chapter, nomenclature_tree=tree)

    def test_process_footnotes_no_footnotes(self):
        chapter = self.roo_mixer.blend(Chapter)

        hierarchy_node = RulesOfOriginMixinModel.objects.create(chapter=chapter)

        rules = Rule.objects.none()
        notes = RulesDocumentFootnote.objects.none()
        processed_footnotes = hierarchy_node.process_footnotes(rules, notes)

        self.assertEqual(processed_footnotes, [])

    def test_process_footnotes_with_footnote(self):
        chapter = self.roo_mixer.blend(Chapter)

        rule = self.roo_mixer.blend(
            Rule, rule_text_processed="This has a footnote [001]."
        )
        note = self.roo_mixer.blend(RulesDocumentFootnote, identifier="001")
        hierarchy_node = RulesOfOriginMixinModel.objects.create(chapter=chapter)

        processed_footnotes = hierarchy_node.process_footnotes([rule], [note])

        self.assertEqual(processed_footnotes, [note])
        self.assertEqual(
            rule.rule_text_processed,
            'This has a footnote <sup><a href="#roo_note_1" class="govuk-link">1)</a></sup>.',
        )

    def test_process_footnotes_with_filtering(self):
        chapter = self.roo_mixer.blend(Chapter)

        rule = self.roo_mixer.blend(
            Rule, rule_text_processed="This has a footnote [002]."
        )
        note_001 = self.roo_mixer.blend(RulesDocumentFootnote, identifier="001")
        note_002 = self.roo_mixer.blend(RulesDocumentFootnote, identifier="002")
        note_003 = self.roo_mixer.blend(RulesDocumentFootnote, identifier="003")
        hierarchy_node = RulesOfOriginMixinModel.objects.create(chapter=chapter)

        processed_footnotes = hierarchy_node.process_footnotes(
            [rule], [note_001, note_002, note_003]
        )

        self.assertEqual(processed_footnotes, [note_002])
        self.assertEqual(
            rule.rule_text_processed,
            'This has a footnote <sup><a href="#roo_note_1" class="govuk-link">1)</a></sup>.',
        )

    def test_process_footnotes_alphabetical_notes(self):
        chapter = self.roo_mixer.blend(Chapter)

        rule = self.roo_mixer.blend(
            Rule, rule_text_processed="This has a footnote [a]."
        )
        note = self.roo_mixer.blend(RulesDocumentFootnote, identifier="001")
        hierarchy_node = RulesOfOriginMixinModel.objects.create(chapter=chapter)

        processed_footnotes = hierarchy_node.process_footnotes([rule], [note])

        self.assertEqual(processed_footnotes, [note])
        self.assertEqual(
            rule.rule_text_processed,
            'This has a footnote <sup><a href="#roo_note_1" class="govuk-link">1)</a></sup>.',
        )

    def test_process_footnotes_alphabetical_notes_filtered(self):
        chapter = self.roo_mixer.blend(Chapter)

        rule = self.roo_mixer.blend(
            Rule, rule_text_processed="This has a footnote [b]."
        )
        note_001 = self.roo_mixer.blend(RulesDocumentFootnote, identifier="001")
        note_002 = self.roo_mixer.blend(RulesDocumentFootnote, identifier="002")
        note_003 = self.roo_mixer.blend(RulesDocumentFootnote, identifier="003")
        hierarchy_node = RulesOfOriginMixinModel.objects.create(chapter=chapter)

        processed_footnotes = hierarchy_node.process_footnotes(
            [rule], [note_001, note_002, note_003]
        )

        self.assertEqual(processed_footnotes, [note_002])
        self.assertEqual(
            rule.rule_text_processed,
            'This has a footnote <sup><a href="#roo_note_1" class="govuk-link">1)</a></sup>.',
        )

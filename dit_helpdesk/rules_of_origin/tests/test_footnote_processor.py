import logging

from django.test import TestCase

from rules_of_origin.footnote_processor import FootnoteReferenceProcessor


logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)


class FootnoteProcessorTestCase(TestCase):
    """
    Test FootnoteReferenceProcessor
    """

    def test_replace_footnote_references_in_rule_text(self):
        footnote_processor = FootnoteReferenceProcessor()

        rule_text = """
            [2][4] Weaving or knitting/crocheting combined with making-up including cutting of
            fabric
            or
            Manufacture from unembroidered fabric (other than knitted or crocheted), provided that
            the value of the unembroidered fabric [3] used does not exceed 40 % of the ex-works
            price
            of the product [2]
        """

        replaced_text = footnote_processor.replace_all_notes_references(rule_text)

        def sup(num):
            return f"<sup>{str(num)})</sup>"

        expected_replaced_text = f"""
            {sup(1)}{sup(2)} Weaving or knitting/crocheting combined with making-up including cutting of
            fabric
            or
            Manufacture from unembroidered fabric (other than knitted or crocheted), provided that
            the value of the unembroidered fabric {sup(3)} used does not exceed 40 % of the ex-works
            price
            of the product {sup(1)}
        """

        self.assertEqual(replaced_text, expected_replaced_text)

        self.assertEqual(len(footnote_processor.unique_note_ids), 3)

        self.assertEqual(footnote_processor.note_number_by_id, {"2": 1, "4": 2, "3": 3})

    def test_replace_footnote_alpha_references_in_rule_text(self):
        footnote_processor = FootnoteReferenceProcessor()

        rule_text = """
            [b][d] Weaving or knitting/crocheting combined with making-up including cutting of
            fabric
            or
            Manufacture from unembroidered fabric (other than knitted or crocheted), provided that
            the value of the unembroidered fabric [c] used does not exceed 40 % of the ex-works
            price
            of the product [b]
        """

        replaced_text = footnote_processor.replace_all_notes_references(rule_text)

        def sup(num):
            return f"<sup>{str(num)})</sup>"

        expected_replaced_text = f"""
            {sup(1)}{sup(2)} Weaving or knitting/crocheting combined with making-up including cutting of
            fabric
            or
            Manufacture from unembroidered fabric (other than knitted or crocheted), provided that
            the value of the unembroidered fabric {sup(3)} used does not exceed 40 % of the ex-works
            price
            of the product {sup(1)}
        """

        self.assertEqual(replaced_text, expected_replaced_text)

        self.assertEqual(len(footnote_processor.unique_note_ids), 3)

        self.assertEqual(footnote_processor.note_number_by_id, {"b": 1, "d": 2, "c": 3})

    def test_replace_footnote_references_in_multiple_rule_texts(self):
        footnote_processor = FootnoteReferenceProcessor()

        rule_text1 = """
            [2][4] Weaving or knitting/crocheting combined with making-up including cutting of
            fabric
            or
            Manufacture from unembroidered fabric (other than knitted or crocheted), provided that
            the value of the unembroidered fabric [3] used does not exceed 40 % of the ex-works
            price
            of the product [2]
        """

        replaced_text1 = footnote_processor.replace_all_notes_references(rule_text1)

        rule_text2 = """
            Example rule with reference to footnote [2] and [5]
        """

        replaced_text2 = footnote_processor.replace_all_notes_references(rule_text2)

        def sup(num):
            return f"<sup>{str(num)})</sup>"

        expected_replaced_text1 = f"""
            {sup(1)}{sup(2)} Weaving or knitting/crocheting combined with making-up including cutting of
            fabric
            or
            Manufacture from unembroidered fabric (other than knitted or crocheted), provided that
            the value of the unembroidered fabric {sup(3)} used does not exceed 40 % of the ex-works
            price
            of the product {sup(1)}
        """
        self.assertEqual(replaced_text1, expected_replaced_text1)

        expected_replaced_text2 = f"""
            Example rule with reference to footnote {sup(1)} and {sup(4)}
        """
        self.assertEqual(replaced_text2, expected_replaced_text2)

        self.assertEqual(len(footnote_processor.unique_note_ids), 4)

        self.assertEqual(
            footnote_processor.note_number_by_id, {"2": 1, "4": 2, "3": 3, "5": 4}
        )

    def test_replace_introducytory_notes_references_in_footnote_text(self):
        footnote_processor = FootnoteReferenceProcessor()

        note_text = """
            For special conditions relating to products made of a mixture of textile materials,
            see @{doc:COMM}[Introductory Note 6].
        """

        replaced_text = footnote_processor.replace_all_introductory_notes_references(
            note_text
        )

        expected_replaced_text = """
            For special conditions relating to products made of a mixture of textile materials,
            see Introductory Note 6 (below).
        """

        self.assertEqual(replaced_text, expected_replaced_text)

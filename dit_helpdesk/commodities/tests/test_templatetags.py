from django.test import TestCase

from commodities.templatetags.cell_cleaner import cell_cleaner
from commodities.templatetags.dotted_format import dotted_format


class TemplateTagsTestCase(TestCase):

    """
    Test Commodities Template Tags
    """

    def test_cell_cleaner_tag_filter_with_empty_value(self):
        result = cell_cleaner("")
        self.assertEqual(result, "-")

    def test_cell_cleaner_tag_filter_with_non_empty_value(self):
        result = cell_cleaner("my value")
        self.assertEqual(result, "my value")

    def test_dotted_format(self):
        self.assertEqual(dotted_format("0123"), "0123")
        self.assertEqual(dotted_format("012345"), "0123.45")
        self.assertEqual(dotted_format("01234567"), "0123.45.67")
        self.assertEqual(dotted_format("0123456789"), "0123.45.67.89")

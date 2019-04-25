from django.template import Context, Template
from django.test import TestCase

from commodities.templatetags.cell_cleaner import cell_cleaner


class TemplateTagsTestCase(TestCase):
    """
    Test Commodities Template Tags
    """

    def test_cell_cleaner_tag_filter_with_empty_value(self):
        result = cell_cleaner('')
        self.assertEqual(result, '-')

    def test_cell_cleaner_tag_filter_with_non_empty_value(self):
        result = cell_cleaner('my value')
        self.assertEqual(result, 'my value')

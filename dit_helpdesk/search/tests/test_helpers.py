from django.test import TestCase

from parameterized import parameterized

from search.helpers import normalise_commodity_code


class HelpersTestCase(TestCase):
    """
    Test Search app config
    """

    @parameterized.expand([
        ("5555", "5555"),
        ("5555.", "5555"),
        ("0123.45", "012345"),
        ("0123..45", "012345"),
        (".", ""),
        ("..", ""),
    ])
    def test_normalise_commodity_code(self, value, normalised):
        self.assertEqual(
            normalise_commodity_code(value), normalised
        )

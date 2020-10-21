from django.test import TestCase

from ..helpers import permute_code_hierarchy


class PermuteCodeHierarchyTestCase(TestCase):
    def test_permute_code_hierarchy(self):
        generator = permute_code_hierarchy("1234567890")

        self.assertEqual(next(generator), "1234567890")
        self.assertEqual(next(generator), "12345678")
        self.assertEqual(next(generator), "123456")
        self.assertEqual(next(generator), "1234")
        self.assertEqual(next(generator), "12")
        with self.assertRaises(StopIteration):
            next(generator)

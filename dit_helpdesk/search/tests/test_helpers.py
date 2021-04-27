from unittest import mock

from mixer.backend.django import mixer
from parameterized import parameterized

from django.test import TestCase

from commodities.models import Commodity
from hierarchy.helpers import create_nomenclature_tree
from hierarchy.models import Heading, SubHeading, Chapter

from search import helpers


class NormaliseCommodityCodeTestCase(TestCase):
    """
    Test Search app config
    """

    @parameterized.expand(
        [
            ("5555", "5555"),
            ("5555.", "5555"),
            ("0123.45", "012345"),
            ("0123..45", "012345"),
            (".", ""),
            ("..", ""),
        ]
    )
    def test_normalise_commodity_code(self, value, normalised):
        self.assertEqual(helpers.normalise_commodity_code(value), normalised)


class GetObjectFromHitTestCase(TestCase):
    def _get_hit(self, index, id, commodity_code):
        hit = mock.MagicMock()
        hit.meta = {"index": index}
        hit.id = id
        hit.__getitem__.side_effect = lambda x: {"commodity_code": commodity_code}[x]

        return hit

    def test_get_object_from_hit(self):
        tree = create_nomenclature_tree("UK")

        chapter = mixer.blend(
            Chapter,
            chapter_code="0100000000",
            goods_nomenclature_sid="1234",
            nomenclature_tree=tree,
        )
        hit = self._get_hit("chapter", "1234", "0100000000")
        found_chapter = helpers.get_object_from_hit(hit)
        self.assertEqual(chapter, found_chapter)

        heading = mixer.blend(
            Heading,
            heading_code="0101000000",
            goods_nomenclature_sid="1234",
            nomenclature_tree=tree,
        )
        hit = self._get_hit("heading", "1234", "0101000000")
        found_heading = helpers.get_object_from_hit(hit)
        self.assertEqual(heading, found_heading)

        subheading = mixer.blend(
            SubHeading,
            commodity_code="0101010000",
            goods_nomenclature_sid="1234",
            nomenclature_tree=tree,
        )
        hit = self._get_hit("subheading", "1234", "0101010000")
        found_subheading = helpers.get_object_from_hit(hit)
        self.assertEqual(subheading, found_subheading)

        commodity = mixer.blend(
            Commodity,
            commodity_code="0101010100",
            goods_nomenclature_sid="1234",
            nomenclature_tree=tree,
        )
        hit = self._get_hit("commodity", "1234", "0101010100")
        found_commodity = helpers.get_object_from_hit(hit)
        self.assertEqual(commodity, found_commodity)

    def test_get_object_from_hit_no_object_found(self):
        hit = self._get_hit("chapter", "1234", "0100000000")
        with self.assertRaises(helpers.ObjectNotFoundFromHit):
            helpers.get_object_from_hit(hit)

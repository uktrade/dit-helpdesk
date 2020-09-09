from mixer.backend.django import mixer

from django.test import TestCase

from commodities.models import Commodity
from hierarchy.models import (
    Chapter,
    Section,
    Heading,
    SubHeading,
)

from ..hierarchy import promote_regulations
from ..models import Regulation


class PromoteRegulationsTestCase(TestCase):
    """
    Test promote_regulations
    """

    def test_models_without_regulations(self):
        model_classes = [
            Chapter,
            Section,
            Heading,
            SubHeading,
            Commodity,
        ]

        for model_class in model_classes:
            obj = mixer.blend(model_class)
            self.assertFalse(obj.regulation_set.exists())
            promote_regulations(obj)
            self.assertFalse(obj.regulation_set.exists())
            obj.delete()

    def test_models_with_regulations(self):
        model_classes = [
            (Chapter, 'chapters'),
            (Section, 'sections'),
            (Heading, 'headings'),
            (SubHeading, 'subheadings'),
            (Commodity, 'commodities'),
        ]

        for model_class, relation_attr in model_classes:
            obj = mixer.blend(model_class)
            regulation = mixer.blend(Regulation, **{relation_attr: obj})

            promote_regulations(obj)
            self.assertEqual(obj.regulation_set.count(), 1)
            self.assertEqual(obj.regulation_set.first(), regulation)

            regulation.delete()
            obj.delete()

import logging
from django.test import TestCase

from mixer.backend.django import mixer
from commodities.models import Commodity
from hierarchy.models import SubHeading, Heading, Section, Chapter
from hierarchy.helpers import create_nomenclature_tree

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.INFO)

models = (Section, Chapter, Heading, SubHeading, Commodity)


class RegionHierarchyManagerTestCase(TestCase):

    """
    Test RegionHierarchyManager
    """

    def setUp(self):
        self.old_eu_tree = create_nomenclature_tree("EU")
        self.eu_tree = create_nomenclature_tree("EU")

        self.old_uk_tree = create_nomenclature_tree("UK")
        self.uk_tree = create_nomenclature_tree("UK")

    def test_retrieval_eu(self):
        for model in models:
            mixer.blend(model, nomenclature_tree=self.eu_tree)
            self.assertFalse(model.objects.all().exists())

    def test_retrieval_uk(self):
        for model in models:
            instance = mixer.blend(model, nomenclature_tree=self.uk_tree)
            self.assertEquals(model.objects.count(), 1)
            self.assertEquals(model.objects.first(), instance)

    def test_retrieval_eu_uk(self):
        for model in models:
            uk_instance = mixer.blend(model, nomenclature_tree=self.uk_tree)
            mixer.blend(model, nomenclature_tree=self.eu_tree)
            self.assertEquals(model.objects.count(), 1)
            self.assertEquals(model.objects.first(), uk_instance)

    def test_retrieval_old_tree(self):
        for model in models:
            mixer.blend(model, nomenclature_tree=self.old_uk_tree)
            new_instance = mixer.blend(model, nomenclature_tree=self.uk_tree)

            self.assertEquals(model.objects.count(), 1)
            self.assertEquals(model.objects.first(), new_instance)


class TreeSelectorMixinTestCase(TestCase):
    def setUp(self):
        self.old_eu_tree = create_nomenclature_tree("EU")
        self.eu_tree = create_nomenclature_tree("EU")
        self.old_uk_tree = create_nomenclature_tree("UK")
        self.uk_tree = create_nomenclature_tree("UK")

    def test_retrieval_eu(self):
        for model in models:
            instance = mixer.blend(model, nomenclature_tree=self.eu_tree)
            self.assertEquals(model.get_active_objects("EU").count(), 1)
            self.assertEquals(model.get_active_objects("EU").first(), instance)

    def test_retrieval_uk(self):
        for model in models:
            uk_instance = mixer.blend(model, nomenclature_tree=self.uk_tree)
            eu_objects = model.get_active_objects("EU")
            uk_objects = model.get_active_objects("UK")
            self.assertFalse(eu_objects.all().exists())
            self.assertEquals(uk_objects.count(), 1)
            self.assertEquals(uk_objects.first(), uk_instance)

    def test_retrieval_eu_uk(self):
        for model in models:
            uk_instance = mixer.blend(model, nomenclature_tree=self.uk_tree)
            eu_instance = mixer.blend(model, nomenclature_tree=self.eu_tree)
            eu_objects = model.get_active_objects("EU")
            uk_objects = model.get_active_objects("UK")

            self.assertEquals(eu_objects.count(), 1)
            self.assertEquals(eu_objects.first(), eu_instance)

            self.assertEquals(uk_objects.count(), 1)
            self.assertEquals(uk_objects.first(), uk_instance)

    def test_retrieval_old_tree(self):
        for model in models:
            mixer.blend(model, nomenclature_tree=self.old_uk_tree)
            uk_instance = mixer.blend(model, nomenclature_tree=self.uk_tree)
            mixer.blend(model, nomenclature_tree=self.old_eu_tree)
            eu_instance = mixer.blend(model, nomenclature_tree=self.eu_tree)
            eu_objects = model.get_active_objects("EU")
            uk_objects = model.get_active_objects("UK")

            self.assertEquals(eu_objects.count(), 1)
            self.assertEquals(eu_objects.first(), eu_instance)

            self.assertEquals(uk_objects.count(), 1)
            self.assertEquals(uk_objects.first(), uk_instance)

            self.assertEquals(model.all_objects.count(), 4)

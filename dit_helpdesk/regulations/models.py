from django.db import models

from .managers import RegulationGroupManager

from hierarchy.models import NomenclatureTree


class RegulationGroup(models.Model):
    """
    Regulation group model
    """

    objects = RegulationGroupManager()

    nomenclature_tree = models.ForeignKey(NomenclatureTree, on_delete=models.CASCADE)

    title = models.TextField()
    sections = models.ManyToManyField("hierarchy.Section")
    chapters = models.ManyToManyField("hierarchy.Chapter")
    headings = models.ManyToManyField("hierarchy.Heading")
    subheadings = models.ManyToManyField("hierarchy.SubHeading")
    commodities = models.ManyToManyField("commodities.Commodity")

    def __str__(self):
        return self.title


class Regulation(models.Model):
    """
    Regulation model
    """

    nomenclature_tree = models.ForeignKey(NomenclatureTree, on_delete=models.CASCADE)

    title = models.TextField()
    regulation_groups = models.ManyToManyField(RegulationGroup)
    type = models.CharField(max_length=255)
    celex = models.CharField(max_length=20)
    url = models.URLField()

    def __str__(self):
        return self.url

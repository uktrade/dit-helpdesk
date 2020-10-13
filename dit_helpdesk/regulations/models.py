import re
import reversion

from django.db import models

from .managers import RegulationGroupManager

from hierarchy.models import NomenclatureTree


@reversion.register()
class RegulationGroup(models.Model):
    """
    Regulation group model
    """

    objects = RegulationGroupManager()

    nomenclature_trees = models.ManyToManyField(NomenclatureTree)

    title = models.TextField()
    sections = models.ManyToManyField("hierarchy.Section")
    chapters = models.ManyToManyField("hierarchy.Chapter")
    headings = models.ManyToManyField("hierarchy.Heading")
    subheadings = models.ManyToManyField("hierarchy.SubHeading")
    commodities = models.ManyToManyField("commodities.Commodity")

    def __str__(self):
        return self.title


@reversion.register()
class Regulation(models.Model):
    """
    Regulation model
    """

    nomenclature_trees = models.ManyToManyField(NomenclatureTree)

    title = models.TextField()
    regulation_groups = models.ManyToManyField(RegulationGroup)
    type = models.CharField(max_length=255)
    celex = models.CharField(max_length=20)
    url = models.URLField()

    VALID_URL_REGEX = r"http:\/\/www.legislation.gov.uk\/(eur|eudn|eudr)\/(?P<year>\d{4})\/(?P<number>\d+)\/contents"

    def __str__(self):
        return self.url

    @property
    def regulation_number(self):
        matches = re.match(self.VALID_URL_REGEX, self.url)

        return f"{matches['number']}/{matches['year']}"

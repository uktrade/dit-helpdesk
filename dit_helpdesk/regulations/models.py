from django.db import models


class Regulation(models.Model):
    """
    Regulation model
    """

    title = models.TextField()
    sections = models.ManyToManyField("hierarchy.Section")
    chapters = models.ManyToManyField("hierarchy.Chapter")
    headings = models.ManyToManyField("hierarchy.Heading")
    subheadings = models.ManyToManyField("hierarchy.SubHeading")
    commodities = models.ManyToManyField("commodities.Commodity")

    class Meta:
        verbose_name_plural = "regulations"

    def __str__(self):
        return self.title


class Document(models.Model):
    """
    Regulation Document model
    """

    title = models.TextField()
    regulations = models.ManyToManyField(Regulation)
    type = models.CharField(max_length=255)
    celex = models.CharField(max_length=20)
    url = models.URLField()

    class Meta:
        verbose_name = "regulation document"
        verbose_name_plural = "regulations documents"

    def __str__(self):
        return self.url

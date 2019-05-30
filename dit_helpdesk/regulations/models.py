from django.db import models


class Regulation(models.Model):
    """
    Regulation model
    """
    title = models.TextField(null=True)
    commodities = models.ManyToManyField("commodities.Commodity")
    subheadings = models.ManyToManyField("hierarchy.SubHeading")

    class Meta:
        verbose_name_plural = "regulations"

    def __str__(self):
        return self.title


class Document(models.Model):
    """
    Regulation Document model
    """
    title = models.TextField(null=True)
    regulations = models.ManyToManyField(Regulation)
    type = models.CharField(max_length=255)
    celex = models.CharField(max_length=20)
    url = models.URLField()

    class Meta:
        verbose_name = "regulation document"
        verbose_name_plural = "regulations documents"

    def __str__(self):
        return self.url

from django.db import models

# Create your models here.


class Regulation(models.Model):

    title = models.TextField()
    sections = models.ManyToManyField("hierarchy.Section")
    commodities = models.ManyToManyField("commodities.Commodity")
    subheadings = models.ManyToManyField("hierarchy.SubHeading")
    headings = models.ManyToManyField("hierarchy.Heading")
    chapters = models.ManyToManyField("hierarchy.Chapter")

    class Meta:
        pass

    def __str__(self):
        return self.title


class Document(models.Model):
    title = models.TextField()
    regulations = models.ManyToManyField(Regulation)
    type = models.CharField(max_length=255)
    celex = models.CharField(max_length=20)
    url = models.URLField()

    class Meta:
        pass

    def __str__(self):
        return self.url

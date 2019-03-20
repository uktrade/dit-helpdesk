from django.db import models

# Create your models here.


class Regulation(models.Model):

    title = models.TextField(null=True)
    sections = models.ManyToManyField("hierarchy.Section")
    commodities = models.ManyToManyField("commodities.Commodity")

    class Meta:
        pass

    def __str__(self):
        return self.title


class Document(models.Model):
    regulations = models.ManyToManyField(Regulation)
    type = models.CharField(max_length=255)
    celex = models.CharField(max_length=20)
    url = models.URLField()

    class Meta:
        pass

    def __str__(self):
        return self.url
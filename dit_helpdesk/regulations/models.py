from django.db import models

# Create your models here.


class Regulation(models.Model):

    type = models.CharField(max_length=255)
    title = models.TextField(null=True)
    celex = models.CharField(max_length=20)
    url = models.URLField()
    sections = models.ManyToManyField("hierarchy.Section")
    commodities = models.ManyToManyField("commodities.Commodity")

    class Meta:
        pass

    def __str__(self):
        return self.title

from django.db import models


class OtherModel(models.Model):
    name = models.CharField(max_length=255)


class ParentModel(models.Model):
    name = models.CharField(max_length=255)
    others = models.ManyToManyField(OtherModel)


class ChildModel(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(ParentModel, null=True, on_delete=models.CASCADE)

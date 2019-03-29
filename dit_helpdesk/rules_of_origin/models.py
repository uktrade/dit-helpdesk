from django.db import models


class Rule(models.Model):
    description = models.TextField()
    right_cell = models.TextField()
    left_cell = models.TextField()

    class Meta:
        verbose_name_plural = "rules"

    def __str__(self):
        return self.description

